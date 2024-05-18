![GitHub](https://img.shields.io/github/license/surquest/python-split-balancer?style=flat-square)
![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/surquest/python-split-balancer/test.yml?branch=main&style=flat-square)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/surquest/373e1859cb547514516a8f22cd8f18a7/raw/python-split-balancer.json&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/surquest-GCP-secret-assessor?style=flat-square)

# Introduction

This project provides a Python package and REST API applications for dividing a set of units into two most comparable groups based on their characteristics.

## Problem Statement

Balancing Numeric Characteristics Across Two Groups

### Input:

* A set of units, where each unit possesses one or more numeric characteristics.
* Desired size for each of the two groups.
* (Optional) Pre-assignment constraints:
    
   - Specify units that must belong to a particular group (Group A or Group B).
   - Specify units that cannot belong to a particular group (Group A or Group B).

### Objective:

Partition the set of units into two groups (Group A and Group B) of the specified size, ensuring maximum similarity between the groups. Similarity is measured by minimizing the sum of absolute differences in mean values for each characteristic across the two groups.

### Constraints:

* Each unit is assigned to either Group A, Group B, or remains unassigned.
* The final size of Group A and Group B must match the specified desired size.

### Output:

* A list of units assigned to Group A and Group B.
* The mean values for each characteristic in Group A and Group B.
* The sum of absolute differences in mean values for each characteristic across the two groups.


## Alternative Math model for pairwise matching 

$$
\begin{equation} 
z = \sum_{i=1}^{N-1}\sum_{j=2}^{N}c_{i,j} x_{i,j} \to MIN 
\end{equation}
$$

$$
\begin{equation} 
\forall_{i} \sum_{j=i+1}^{N }x_{i,j} = a_{i}  \qquad i=1,2, ..., N-1
\end{equation}
$$

$$
\begin{equation} 
\forall_{j} \sum_{i=1}^{j-1 }x_{i,j} = b_{j}  \qquad j=2, 3, ..., N
\end{equation}
$$

$$
\begin{equation} 
\sum_{i=1}^{N-1}a_{i} =  T
\end{equation}
$$

$$
\begin{equation} 
\sum_{j=2}^{N}b_{j} =  C
\end{equation}
$$

| | |$_{2}$|$_{3}$|$_{4}$|...|...|$_{j}$|...|$_{N}$| | | |
|--|--|--|--|--|--|--|--|--|--|--|--|--|
| $_{1}$ |  | $x_{1,2}$ | $x_{1,3}$ | $x_{1,4}$ | ... |... | $x_{1,j}$ | ... | $x_{1,N}$ | = | $a_{1}$ |
| $_{2}$ |  | - | $x_{2,3}$| $x_{2,4}$| ... | ... | $x_{2,j}$| ... | $x_{2,N}$ | = | $a_{2}$ |
| $_{3}$ |  | - | - | $x_{3,4}$|...| ... | $x_{3,j}$| ... | $x_{3,N}$ | = | $a_{3}$ |
| $_{4}$ |  | - | - | - | - | - | $x_{4,j}$| ... | $x_{4,N}$ | = | $a_{4}$ |
| | | | | | | | | | | | | |
| $_{i}$ |  | - | - | - | - | - | $x_{i,j}$ | ... | $x_{i,N}$| = | $a_{i}$ |
| | | | | | | | | | | | | |
| $_{N-1}$ |  | - | - | - | - | - | - | - | $x_{N-1,N}$| = | $a_{N-1}$ |
| | | | | | | | | | | | = $T$ |
| | | | | | | | | | | | | |
| | | = | = | = | | | = | | = | | |
| | | $b_{2}$ | $b_{3}$ | $b_{4}$ | ... |... | $b_{j}$ | ... | $b_{N}$ | | = $C$ |

# Local development

You are more than welcome to contribute to this project. To make your start easier we have prepared a docker image with all the necessary tools to run it as interpreter for Pycharm or to run tests.


## Build docker image
```
docker build `
     --tag surquest/surquest/split-balancer:latest `
     --file package.base.dockerfile `
     --target test .
```


## Run docker container
```
docker run --rm -it `
 -v "${pwd}:/opt/project" `
 -w "/opt/project/test" `
 surquest/surquest/split-balancer:latest pytest
```


# REST API Quick Start

```powershell

# Build the docker image

docker build `
     --no-cache `
     --tag surquest/app-split-balancer:latest `
     --file app.base.dockerfile `
     --target base .

docker build `
     --no-cache `
     --tag surquest/app-split-balancer:latest `
     --file app.base.dockerfile `
     --target app .

# Run the docker container
docker run --rm -it `
    --name split-balancer `
    -v "$(pwd):/opt/project" `
    -p 1010:8080 surquest/app-split-balancer:latest
```