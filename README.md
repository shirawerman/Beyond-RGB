# Beyond-RGB
A real- world dataset comprising thousands of multispectral and RGB images in diverse real world and lab conditions.
Dataset: [https://1drv.ms/u/s!AheBo1Cre0p_gYhXovaSSrG3LNo1Pg?e=V17jcM](url)
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

- field (field images, outdoor and indoor)
  - 1
    -  CRI
    -  NT
    -  WT
  - ...
