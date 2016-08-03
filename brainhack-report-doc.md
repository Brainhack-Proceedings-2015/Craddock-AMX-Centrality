
Optimized implementations of voxel-wise degree centrality and local functional connectivity density mapping in AFNI
===================================================================================================================


Report from 2015 Brainhack Americas (MX)
----------------------------------------


R. Cameron Craddock^1^^,^^2^*, Daniel J. Clark^2^


^1^Computational Neuroimaging Lab, Center for Biomedical Imaging and Neuromodulation, Nathan Kline Institute for Psychiatric Research, Orangeburg, New York, USA

^2^Center for the Developing Brain, Child Mind Institute, New York, New York, USA

*Email: ccraddock@nki.rfmh.org





#Introduction

Degree centrality (DC) [1] and local functional connectivity density (lFCD) [2] are statistics calculated from brain connectivity graphs that measure how important a brain region is to the graph. DC (a.k.a. global functional connectivity density [2]) is calculated as the number of connections a region has with the rest of the brain (binary DC), or the sum of weights for those connections (weighted DC) [1]. lFCD was developed to be a surrogate measure of DC that is faster to calculate by restricting its computation to regions that are spatially adjacent [2]. Although both of these measures are popular for investigating inter-individual variation in brain connectivity, efficient neuroimaging tools for computing them are scarce. The goal of this Brainhack project was to contribute optimized implementations of these algorithms to the widely used, open source, AFNI software package [3]



#Approach

Tools for calculating DC (`3dDegreeCentrality` and lFCD (`3dLFCD` were implemented by modifying the C source code of AFNI's `3dAutoTcorrelate` tool. `3dAutoTcorrelate` calculates the voxel \times voxel correlation matrix for a dataset and includes most of the functionality we require, including support for OpenMP [4] multithreading to improve calculation time, the ability to restrict the calculation using a user-supplied or auto-calculated mask, and support for both Pearson's and Spearman correlation.



##### `3dDegreeCentrality`

Calculating DC is straight forward and is quick when a correlation threshold or is used. In this scenario, each of the .5*N_{vox}*(N_{vox}-1) unique correlations are calculated, and if they exceed a user specified threshold (default threshold = 0.0) the binary and weighted DC value for each of the voxels involved in the calculation are incremented. The procedure is more tricky if sparsity thresholding is used, where the top P\% of connections are included in the calculation. This requires that a large number of the connections be retained and ranked - consuming substantial memory and computation. We optimize this procedure with a histogram and adaptive thresholding. If a correlation exceeds threshold it is added to a 50-bin histogram (array of linked lists). If it is determined that the lowest bin of the histogram is not needed to meet the sparsity goal, the threshold is increased by the bin-width and the bin is discarded. Once all of the correlations have been calculated, the histogram is traversed from high to low, incorporating connections into binary and weighted DC until a bin is encountered that would push the number of retained connections over the desired sparsity. This bin's values are sorted into a 100-bin histogram that is likewise traversed until the sparsity threshold is met or exceeded. The number of bins in the histograms effects the computation time and determine the precision with which ties between voxel values are broken. A greater number of bins allow the sparsity threshold to be determined more precisely but will take longer to converge. Fewer bins will result in faster computation but will increase the tendency of the algorithm to return more voxels than requested. The chosen parameters enable ties to be broken with a precision of 1.0/(50*100), which in our experience offers quick convergence and a good approximation of the desired sparsity.







| Impl|Thr|Mem (GB)    | T_D (s) |Mem (GB)    |T_D (s)    | Mem (GB)   |T_D (s)  |

|-----+---+------------+-----------+------------+-------------+------------+-----------|

|C-PAC|  1|2.17 (0.078)|67.7 (3.90)|5.62 (0.176)|342.2 (12.25)|2.16 (0.082)|88.3 (6.40)|

|AFNI |  1|0.84 (0.003)|62.6 (9.23)|0.85 (0.002)|86.3 (13.83) |0.86 (0.003)|8.8 (1.27) |

|AFNI |  2|0.86 (0.002)|39.0 (4.62)|0.86 (0.003)|38.2 (0.55)  |0.86 (0.003)|5.1 (0.25) |

|AFNI |  4|0.86 (0.003)|18.2 (1.93)|0.87 (0.003)|19.0 (0.45)  |0.87 (0.003)|4.3 (0.23) |

|AFNI |  8|0.87 (0.002)|11.2 (0.25)|0.87 (0.000)|11.3 (0.31)  |0.87 (0.000)|4.1 (0.15) |



|     |    | r > 0.6 | 0.1 Sparsity |



##### `3dLFCD`

lFCD was calculating using a region growing algorithm in which face-, side-, and corner-touching voxels are iteratively added to the cluster if their correlation with the target voxel exceeds a threshold (default threshold = 0.0). Although lFCD was originally defined as the number of voxels locally connected to the target, we also included a weighted version.



##### Validation:

Outputs from the newly developed tools were benchmarked to Python implementations of these measures from the Configurable Pipeline for the Analysis of Connectomes (C-PAC) [5] using in the publically shared Fig. 1  Brain Activity Test-Retest (IBATRT) dataset} from the Consortium for Reliability and Reproduciblity[6]



#Results

AFNI tools were developed for calculating lFCD and DC from functional neuroimaging data and have been submitted for inclusion into AFNI. LFCD and DC maps from the test dataset (illustrated in Fig. Fig. 2  are highly similar to those calculated using C-PAC (spatial concordance correlation [7] \rho \geq 0.99 ) but required substantially less time and memory (see Table Fig. 3 



![Figure 1. Whole brain maps of binarized and weighted degree centrality calculated with a correlation threshold of r > 0.6 (a-b) and sparsity threshold of 0.1\% (c-d) and binarized and weighted lFCD calculated with a correlation threshold of r > 0.6 (e-f) averaged across maps calculated the first resting state scan of the first scanning session for all 36 participants' data from the IBATRT data. ](centrality_plot2.png)



# Conclusions

Optimized versions of lFCD and DC achieved 4\times to 10\times decreases in computation time compared to C-PAC's Python implementation and decreased the memory footprint to less than 1 gigabyte. These improvements will dramatically increase the size of Connectomes analyses that can be performed using conventional workstations. Making this implementation available through AFNI ensures that it will be available to a wide range of neuroimaging researchers who do not have the wherewithal to implement these algorithms themselves.


###Availability of Supporting Data
More information about this project can be found at: http://github.com/ccraddock/afni

###Competing interests
None

###Author's contributions
RCC and DJC wrote the software, DJC performed tests, and DJC and RCC wrote the report.

###Acknowledgements
The authors would like to thank the organizers and attendees of Brainhack MX and the developers of AFNI. This project was funded in part by a Educational Research Grant from Amazon Web Services.

###References


1. Rubinov M, Sporns O. Complex network measures of brain connectivity: uses and interpretations. Neuroimage. 2010; 52: 1059-1069.
2. Tomasi D, Volkow ND. Functional connectivity density mapping. Proc Natl Acad Sci USA. 2010; 107: 9885-9890.
3. Cox RW. AFNI: software for analysis and visualization of functional magnetic resonance neuroimages. Comput Biomed Res. 1996; 29: 162-173.
4. Dagum Leonardo, Menon Ramesh. OpenMP: an industry standard API for shared-memory programming. Computational Science \& Engineering, IEEE. 1998; 5: 46-55.
5. Craddock Cameron,  Sikka Sharad,  Cheung Brian,  Khanuja Ranjeet,  Ghosh Satrajit S,  Yan Chaogan,  Li Qingyang,  Lurie Daniel,  Vogelstein Joshua,  Burns R,al,  Colcombe Stanley,  Mennes Maarten,  Kelly Clare,  Di Martino Adriana,  Castellanos Francisco Xavier,  Milham Michael. Towards Automated Analysis of Connectomes: The Configurable Pipeline for the Analysis of Connectomes (C-PAC). Frontiers in Neuroinformatics. 2013; .
6. Xi-Nian Zuo, Jeffrey S Anderson, Pierre Bellec, Rasmus M Birn, Bharat B Biswal, Janusch Blautzik, John CS Breitner, R,y L Buckner, Vince D Calhoun, FXavier Castellanos, Antao Chen, Bing Chen, Jiangtao Chen, Xu Chen, Stanley J Colcombe, William Courtney, RCameron Craddock, Adriana Di Martino, Hao-Ming Dong, Xiaolan Fu, Qiyong Gong, Krzysztof J Gorgolewski, Ying Han, Ye He, Yong He, Erica Ho, Avram Holmes, Xiao-Hui Hou, Jeremy Huckins, Tianzi Jiang, Yi Jiang, William Kelley, Clare Kelly, Margaret King, Stephen M LaConte, Janet E Lainhart, Xu Lei, Hui-Jie Li, Kaiming Li, Kuncheng Li, Qixiang Lin, Dongqiang Liu, Jia Liu, Xun Liu, Yijun Liu, Guangming Lu, Jie Lu, Beatriz Luna, Jing Luo, Daniel Lurie, Ying Mao, Daniel S Margulies, Andrew R Mayer, Thomas Meindl, Mary E Meyer,, Weizhi Nan, Jared A Nielsen, David O'Connor, David Paulsen, Vivek Prabhakaran, Zhigang Qi, Jiang Qiu, Chunhong Shao, Zarrar Shehzad, Weijun Tang, Arno Villringer, Huiling Wang, Kai Wang, Dongtao Wei, Gao-Xia Wei, Xu-Chu Weng, Xuehai Wu, Ting Xu, Ning Yang, Zhi Yang, Yu-Feng Zang, Lei Zhang, Qinglin Zhang, Zhe Zhang, Zhiqiang Zhang, Ke Zhao, Zonglei Zhen, Yuan Zhou, Xing-Ting Zhu, Michael P Milham. An open science resource for establishing reliability and reproducibility in functional connectomics. Scientific Data. 2014; 1: 140049.
7. Lange N, Strother SC, Anderson JR, Nielsen FA, Holmes AP, Kolenda T, Savoy R, Hansen LK. Plurality and resemblance in fMRI data analysis. Neuroimage. 1999; 10: 282-303.
