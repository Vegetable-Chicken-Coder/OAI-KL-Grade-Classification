# About
This Repo contains code for paper **Attention-based CNN for KL Grade Classification: Data from the Osteoarthritis Initiative**
# Repo structure
* `./data` contains data for training/testing data for detector and classifier. `OAI_summary.csv` file is from OAI dataset, and contains metadata for all patients. The train/test split gave the performance mentioned in paper.
* `./model_weights` contains model weights that can be readily used by `torch.load` with the performance mentioned in paper.
* `./oai-knee-detection` contains code to train a detector and generate all annotations
* `./oai-xray-klg` contains code to train classifier and generate the attention map from GradCAM

# Instruction
Please refer to `requirements.txt` for install all dependencies for this project. `./data` folder contains example content file for train/test data used in dataloader for both detector and classifier. `./model_weights` folder contains model weights that achieved the performance metrics mentioned in paper.

This repo consists of two parts. To reproduce the entire experiments, you will need to
1. Train a detector and use the detector to annotate all OAI dataset, and generate train/test data for the classifier. See documentation in `./oai-knee-detection`.
2. Train and test the classifier by following documentation in `./oai-xray-klg`

# How to cite
```latex
@inproceedings{zhang2020attention,
  title={Attention-based cnn for kl grade classification: Data from the osteoarthritis initiative},
  author={Zhang, Bofei and Tan, Jimin and Cho, Kyunghyun and Chang, Gregory and Deniz, Cem M},
  booktitle={2020 IEEE 17th International Symposium on Biomedical Imaging (ISBI)},
  pages={731--735},
  year={2020},
  organization={IEEE}
}
```
