# Beyond-RGB
A real- world dataset comprising thousands of multispectral and RGB images in diverse real world and lab conditions.

Note that the paper describing this dataset is avaliable here: [https://openaccess.thecvf.com/content/WACV2024/papers/Glatt_Beyond_RGB_A_Real_World_Dataset_for_Multispectral_Imaging_in_WACV_2024_paper.pdf.](https://openaccess.thecvf.com/content/WACV2024/html/Glatt_Beyond_RGB_A_Real_World_Dataset_for_Multispectral_Imaging_in_WACV_2024_paper.html) 

When publishing results based on this database, please cite it as:

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


Dataset:

[https://1drv.ms/u/s!AheBo1Cre0p_gYhXovaSSrG3LNo1Pg?e=V17jcM](url)

File hashes: 

c8a9cc9a0e50c9e9df988bf6814ac2a15cff84b9f649f889656d04aa64cb0052

f4b36f3302ce8d6c83e4ec76f7b2c1b9

Directory tree **beyondRGB**:

- clb (lab images)
    
  - BLUE_blue (scene colors)
  
    
    - 1_light1 (illuminant numbering)
      
        -   CRI (Spectophotometer measurements)
          
        -   NT
          
          -   MIS.h5 (Multispectral image)
            
          -   oppo.h5 (Oppo phone camera raw image)
      
          -   oppo_tags.json (Oppo metadata)
      
          -   samsung.h5 (Samsung phone camera raw image)
      
          -   samsung_tags.json (Samsung metadata)
      
        -   WT
        
          - MIS.h5
        
          - MIS_cc_detection.json (color chart patches' positions in multispectral image)

          - oppo.h5

          - oppo_cc_detection.json (color chart patches' positions in oppo image)

          - oppo_tags.json

          - samsung.h5

          - samsung_cc_detection.json (color chart patches' positions in samsung image)

          - samsung_tags.json
      
    - ...
        
  -  ...

- outdoor (field images, outdoor and indoor)
  - 1
    -  CRI
    -  NT
    -  WT
  - ...

For privacy reasons faces and car plates were blurred. Images with blurred regions have a corresponding json which contains the blurr bounding box regions.
