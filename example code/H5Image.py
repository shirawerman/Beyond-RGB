import numpy as np
import colour
import h5py as h5
import json
import ast
import re
from colour.temperature import xy_to_CCT_McCamy1992
from pathlib import Path
from functools import cached_property

"""
Sources:

DNG Spec v1.6: 
https://helpx.adobe.com/content/dam/help/en/photoshop/pdf/dng_spec_1_6_0_0.pdf

Tutorial paper:
Rowlands, Color conversion matrices in digital cameras: a tutorial
https://www.spiedigitallibrary.org/journals/optical-engineering/volume-59/issue-11/110801/Color-conversion-matrices-in-digital-cameras-a-tutorial/10.1117/1.OE.59.11.110801.full?SSO=1
"""

CCS_D50 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["D50"]
CCS_D55 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["D55"]
CCS_D65 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["D65"]
CCS_D75 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["D75"]
CCS_E = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["E"]
CCS_A = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["A"]
CCS_B = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["B"]
CCS_C = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["C"]
CCS_TUNGSTEN = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']["ISO 7589 Studio Tungsten"]

ILLUMINANTS = {
    # Illuminants which are commented out don't have a clear mapping to CCS_ILLUMINANTS, they are left as they appear in the spec definition.
    # 0: "Unknown",
    # 1: "Daylight",
    # 2: "Fluorescent",
    # 3: "Tungsten (incandescent light)",
    # 4: "Flash",
    # 9: "Fine weather",
    # 10: "Cloudy weather",
    # 11: "Shade",
    # 12: "Daylight fluorescent (D 5700 - 7100K)",
    # 13: "Day white fluorescent (N 4600 - 5400K)",
    # 14: "Cool white fluorescent (W 3900 - 4500K)",
    # 15: "White fluorescent (WW 3200 - 3700K)",
    17: CCS_A,
    18: CCS_B,
    19: CCS_C,
    20: CCS_D55,
    21: CCS_D65,
    22: CCS_D75,
    23: CCS_D50,
    24: CCS_TUNGSTEN,
    # 255: "Other light source",
}


class H5Image(object):
    def __init__(self, h5_fpath: Path, json_fpath: Path):
        self.fpath = h5_fpath
        self.json_fpath = json_fpath

        h5_file = h5.File(str(h5_fpath), 'r')
        image_key = [k for k in h5_file][0]
        self.demosaiced_image = np.array(h5_file[image_key])

        with open(json_fpath, 'r') as file:
            self.tags = json.load(file)

        for tag in self.tags:
            try:
                self.tags[tag] = self._parse_tag(self.tags[tag])
            except Exception as e:
                pass

        self.alpha, self.cct = self._interpolate_color_matrix(self.as_shot_neutral)

    @staticmethod
    def _parse_tag(tag_str):
        try:
            tag = ast.literal_eval(tag_str)
        except (SyntaxError):
            tag = np.array([float(x) for x in re.findall(r'-?\d+\.?\d*', tag_str)])
        return tag

    def _interpolate_color_matrix(self, as_shot_neutral: np.array, neutral_is_in_reference_space: bool = True):
        """
        This method performs the "self consistent" iteration procedure to find the correct interpolation value ("alpha") for the scene illuminant.
        The interpolation value is later used to interpolate the correct color matrix (CM), forward matrix (FM) and calibration matrix (CC).
        The algorithm is described in the tutorial paper in section 7.3.

        Inputs:
        as_shot_neutral:
        --> 3 element vector indicating the (R,G,B) whitepoint in the <reference sensor space> or <specific camera space>.

        neutral_is_in_reference_space:
        --> True, <as_shot_neutral> is already in the reference space. This is the case when using the DNG "AsShotNeutral" field.
        --> False, <as_shot_neutral> is in raw <specific camera space>. This is the case when using a white-patch found in the image after applying only demosaicing.

        Returns:
            alpha - a float in the range [0,1], which is the interpolation parameter for the FM, CM and CC matrices.
            CCT - the estimated correlated color temperature to which the solution converged.
        """
        cRGB_wp = as_shot_neutral
        cRGB_wp = cRGB_wp / cRGB_wp[1]

        cm1 = self.color_matrix1
        cc1 = self.camera_calibration1
        cct1 = self.calibration_illuminant1_cct

        cm2 = self.color_matrix2
        cc2 = self.camera_calibration2
        cct2 = self.calibration_illuminant2_cct

        # ================= Prepare Conversion Matrices =================#
        # ===============================================================#
        # Initial condition - average of CCT1/CCT2:
        cct = (cct1 + cct2) / 2
        delta = 10e3
        count = 0

        while delta > 1 and count <= 30:
            if cct > cct1:  # high temperature illuminant
                alpha = 0
            elif cct < cct2:  # low temperature illuminant
                alpha = 1
            else:
                alpha = (1 / cct - 1 / cct1) / (1 / cct2 - 1 / cct1)

            cm = alpha * cm2 + (1 - alpha) * cm1
            cc = alpha * cc2 + (1 - alpha) * cc1

            if neutral_is_in_reference_space:
                cRGB_to_XYZ = np.linalg.inv(cm)
            else:
                cRGB_to_XYZ = np.linalg.inv(cc @ cm)

            new_cct = xy_to_CCT_McCamy1992(colour.XYZ_to_xy(cRGB_to_XYZ @ cRGB_wp))
            delta = np.abs(new_cct - cct)

            cct = new_cct

            count += 1

        return alpha, cct

    def _retrieve_tag(self, prop_name):
        if prop_name in self.tags:
            return self.tags[prop_name]
        else:
            raise KeyError(f'{prop_name} field does not exist in this DNG file.')

    @property
    def camera_model(self) -> str:
        return self._retrieve_tag('UniqueCameraModel')

    @cached_property
    def color_matrix1(self):
        # XYZ --> cRGB at illuminant 1 (usually D65)
        return np.reshape(self._retrieve_tag('ColorMatrix1'), (3, -1))

    @cached_property
    def color_matrix2(self):
        # XYZ --> cRGB at illuminant 2 (usually A)
        return np.reshape(self._retrieve_tag('ColorMatrix2'), (3, -1))

    @cached_property
    def camera_calibration1(self):
        cc = self._retrieve_tag('CameraCalibration1')
        if len(cc) == 3:
            return np.diag(cc)
        else:
            return np.reshape(cc, (3, -1))

    @cached_property
    def camera_calibration2(self):
        cc = self._retrieve_tag('CameraCalibration2')
        if len(cc) == 3:
            return np.diag(cc)
        else:
            return np.reshape(cc, (3, -1))

    @cached_property
    def calibration_illuminant1(self):
        return ILLUMINANTS[self._retrieve_tag('CalibrationIlluminant1')]

    @cached_property
    def calibration_illuminant2(self):
        return ILLUMINANTS[self._retrieve_tag('CalibrationIlluminant2')]

    @cached_property
    def calibration_illuminant1_cct(self):
        return xy_to_CCT_McCamy1992(self.calibration_illuminant1)

    @cached_property
    def calibration_illuminant2_cct(self):
        return xy_to_CCT_McCamy1992(self.calibration_illuminant2)

    @cached_property
    def forward_matrix1(self):
        return np.reshape(self._retrieve_tag('ForwardMatrix1'), (3, -1))

    @cached_property
    def forward_matrix2(self):
        return np.reshape(self._retrieve_tag('ForwardMatrix2'), (3, -1))

    @cached_property
    def as_shot_neutral(self):
        return np.array(self._retrieve_tag('AsShotNeutral'))

    @cached_property
    def has_forward_matrices(self):
        if 'ForwardMatrix1' in self.tags and 'ForwardMatrix2' in self.tags:
            return True
        else:
            return False

    @cached_property
    def awb_estimated_xyz(self):
        CM = self.alpha * self.color_matrix2 + (1 - self.alpha) * self.color_matrix1

        return np.linalg.inv(CM) @ self.as_shot_neutral

    @cached_property
    def white_balanced_image(self) -> np.ndarray:
        """
        Returns an sRGB-D65 white-balanced image according to the camera AWB estimate included in the DNG file.
        """
        return self._white_balanced_image(cRGB_wp=self.as_shot_neutral, alpha=self.alpha, apply_gamma=True)

    @cached_property
    def white_balanced_image_linear_RGB(self) -> np.ndarray:
        return self._white_balanced_image(cRGB_wp=self.as_shot_neutral, alpha=self.alpha, apply_gamma=False)

    def _white_balanced_image(self, cRGB_wp: np.array, alpha: float, apply_gamma: bool):
        """
        Apply white-balance given the scene white-point in cRGB (reference camera space).
        Uses forward matrices if available and color matrices otherwise.
        """
        if self.has_forward_matrices:
            # DNG Spec v1.6 pg. 88
            # Tutorial paper section 7.4
            D = np.diag(1 / cRGB_wp / cRGB_wp[1])
            FM = alpha * self.forward_matrix2 + (1 - alpha) * self.forward_matrix1
            CC = alpha * self.camera_calibration2 + (1 - alpha) * self.camera_calibration1

            # Forward matrix method returns an image in XYZ space with D50 white point.
            XYZ_D50 = np.einsum('ij,hwj->hwi', FM @ D, self.demosaiced_image)

            # Convert to sRGB D65 while also applying Bradford chromatic adaptation from the D50 white-point:
            sRGB65 = colour.XYZ_to_sRGB(XYZ_D50, illuminant=CCS_D50, chromatic_adaptation_transform='Bradford',
                                        apply_cctf_encoding=apply_gamma)
        else:
            # DNG Spec v1.6 pg. 87
            # Tutorial paper section 7.1-7.3
            CM = alpha * self.color_matrix2 + (1 - alpha) * self.color_matrix1
            CC = alpha * self.camera_calibration2 + (1 - alpha) * self.camera_calibration1

            rRGB_to_XYZ = np.linalg.inv(CM)  # The <reference sensor space> to XYZ transform.
            cRGB_to_XYZ = np.linalg.inv(CC @ CM)  # The <specific camera space> to XYZ transform.
            scene_illuminant_xyz = rRGB_to_XYZ @ cRGB_wp  # As shot neutral is already in <reference sensor space>, convert it to XYZ so we have the estimated AW.

            # Color matrix method returns an XYZ image with the "auto-white" (AW) whitepoint:
            XYZ_AW = np.einsum('ij,hwj->hwi', cRGB_to_XYZ, self.demosaiced_image)

            # Convert to sRGB D65 while also applying Bradford chromatic adaptation from the AW white-point:
            sRGB65 = colour.XYZ_to_sRGB(XYZ_AW, illuminant=colour.XYZ_to_xy(scene_illuminant_xyz),
                                        apply_cctf_encoding=apply_gamma)

        return np.clip(sRGB65, 0, 1)

    def apply_external_white_balance_white_patch(self, cRGB_wp: np.array, apply_gamma=False) -> np.ndarray:
        """
        Apply an external white-balance where the expected input is a grey-tone from the RAW scene.

        cRGB_wp: a vector with 3 elements whose values represent a gray tone in the RAW image (as returned by self.demosaiced_image, for example).

        apply_gamma: <True> apply standard sRGB gamma to the returned image, <False> return a linear sRGB image.

        Returns:
        A white balanced image in sRGB space with D65 white point.
        """
        # Find the interpolation parameter; since this is meant to be used with the RAW image we indicate that cRGB_wp is *not* in the <reference camera space> and is assumed to be in the <specific camera space>.
        alpha, _ = self._interpolate_color_matrix(cRGB_wp, neutral_is_in_reference_space=False)

        return self._white_balanced_image(cRGB_wp=cRGB_wp, alpha=alpha, apply_gamma=apply_gamma)

    def apply_external_white_balance(self, xy_external: np.array, apply_gamma=False) -> np.ndarray:
        """
        Apply an externally measured whitebalance for illuminant with coordinates (x,y).

        xy_external: a vector with 2 elements that represents the (x,y) value of the measured illuminant.

        apply_gamma: <True> apply standard sRGB gamma to the returned image, <False> return a linear sRGB image.

        Returns:
        A white balanced image in sRGB space with D65 white point.
        """
        cm1 = self.color_matrix1
        cct1 = self.calibration_illuminant1_cct

        cm2 = self.color_matrix2
        cct2 = self.calibration_illuminant2_cct

        # Correlated color temperature of the given (x,y) illuminant:
        cct_external = xy_to_CCT_McCamy1992(xy_external)

        # Go back from CCT to (x,y) to get a white-point that is exactly on the CCT locus:
        xy_external_on_CCT = colour.temperature.CCT_to_xy(cct_external)
        xyz_external_on_CCT = colour.xy_to_XYZ(xy_external_on_CCT)

        if cct_external > cct1:  # high temperature illuminant
            alpha = 0
        elif cct_external < cct2:  # low temperature illuminant
            alpha = 1
        else:
            alpha = (1 / cct_external - 1 / cct1) / (1 / cct2 - 1 / cct1)

        CM = alpha * cm2 + (1 - alpha) * cm1

        # Convert the external XYZ measurement to cRGB (reference sensor space) so that it can be used in the same manner as "AsShotNeutral":
        cRGB_wp = CM @ xyz_external_on_CCT

        return self._white_balanced_image(cRGB_wp=cRGB_wp, alpha=alpha, apply_gamma=apply_gamma)

    @staticmethod
    def color_adaptation_matrix_bradford(source_white_xyz: np.array, dest_white_xyz: np.array) -> np.array:
        """
        Returns the Bradford color adaptation matrix from source_white_xyz to dest_white_xyz.
        http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
        """
        # Assume 2 element vectors are xy
        if source_white_xyz.size == 2:
            source_white_xyz = colour.xy_to_XYZ(source_white_xyz)

        if dest_white_xyz.size == 2:
            dest_white_xyz = colour.xy_to_XYZ(dest_white_xyz)

        Ma = colour.adaptation.CAT_BRADFORD

        R_source = Ma @ source_white_xyz
        R_dest = Ma @ dest_white_xyz

        return np.linalg.inv(Ma) @ np.diag(R_dest / R_source) @ Ma
