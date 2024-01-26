# Beyond-RGB
A real- world dataset comprising thousands of multispectral and RGB images in diverse real world and lab conditions.
All the scenes in our dataset include a colorimetric reference and a measurement of the spectrum of the scene illuminant.

The dataset is introduced in ***Beyond RGB: A Real World Dataset for Multispectral Imaging in Mobile Devices*** paper, available here:
[https://openaccess.thecvf.com/content/WACV2024/papers/Glatt_Beyond_RGB_A_Real_World_Dataset_for_Multispectral_Imaging_in_WACV_2024_paper.pdf.](https://openaccess.thecvf.com/content/WACV2024/html/Glatt_Beyond_RGB_A_Real_World_Dataset_for_Multispectral_Imaging_in_WACV_2024_paper.html) 

<p align="center">
  <img width="750px" src="https://github.com/shirawerman/Beyond-RGB/blob/main/imgs/field_git.png" alt="Sample field images from Beyond RGB dataset"><br>
    Sample lab images from Beyond RGB dataset
</p>


<p align="center">
  <img width="750px" src="https://github.com/shirawerman/Beyond-RGB/blob/main/imgs/clb_git.png" alt="Sample lab images from Beyond RGB dataset"><br>
    Sample lab images from Beyond RGB dataset
</p>

When using this dataset, please cite:

```

@InProceedings{Glatt_2024_WACV,
    author    = {Glatt, Ortal and Ater, Yotam and Kim, Woo-Shik and Werman, Shira and Berby, Oded and Zini, Yael and Zelinger, Shay and Lee, Sangyoon and Choi, Heejin and Soloveichik, Evgeny},
    title     = {Beyond RGB: A Real World Dataset for Multispectral Imaging in Mobile Devices},
    booktitle = {Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)},
    month     = {January},
    year      = {2024},
    pages     = {4344-4354}
}

```

Dataset download is available via

[https://1drv.ms/u/s!AheBo1Cre0p_gYhXovaSSrG3LNo1Pg?e=V17jcM](https://1drv.ms/u/s!AheBo1Cre0p_gYhXovaSSrG3LNo1Pg?e=V17jcM)


For verification the file hashes for the zip file are:

sha256: c8a9cc9a0e50c9e9df988bf6814ac2a15cff84b9f649f889656d04aa64cb0052

md5: f4b36f3302ce8d6c83e4ec76f7b2c1b9


<br/><br/>
**Beyond RGB dataset folders structure**:

- clb (lab images)
    
  - BLUE_blue (scene colors)
  
    
    - 1_light1 (illuminant numbering)
      
        -   CRI
          
          -   CRI.txt (illuminant Spectophotometer measurement)
          
        -   NT
          
          -   MIS.h5 (Multispectral raw image)
            
          -   oppo.h5 (Oppo phone camera raw image)
      
          -   oppo_tags.json (Oppo image metadata)
      
          -   samsung.h5 (Samsung phone camera raw image)
      
          -   samsung_tags.json (Samsung image metadata)
      
        -   WT
        
          - MIS.h5 (Multispectral raw image)
        
          - MIS_cc_detection.json (color chart patches' positions in multispectral image)

          - oppo.h5 (Oppo phone camera raw image)

          - oppo_cc_detection.json (color chart patches' positions in oppo image)

          - oppo_tags.json (Oppo image metadata)

          - samsung.h5 (Samsung phone camera raw image)

          - samsung_cc_detection.json (color chart patches' positions in samsung image)

          - samsung_tags.json (Samsung image metadata)
      
    - ...
        
  -  ...

- outdoor (field images, outdoor and indoor)
  - 1 (scene numbering)
    -  CRI
    -  NT
    -  WT
  - ...

[For privacy reasons faces and car plates were blurred. Images with blurred areas have a corresponding json file, which contains the blurred areas bounding boxes (\<device\>_blurred_areas_detection.json).]
