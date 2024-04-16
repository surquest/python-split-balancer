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

Partition the units into two groups (Group A and Group B) of the specified size, ensuring maximum similarity between the groups. Similarity is measured by minimizing the sum of absolute differences in mean values for each characteristic across the two groups.

### Constraints:

* Each unit is assigned to either Group A, Group B, or remains unassigned.
* The final size of Group A and Group B must match the specified desired size.

### Output:

* A list of units assigned to Group A and Group B.
* The mean values for each characteristic in Group A and Group B.
* The sum of absolute differences in mean values for each characteristic across the two groups.


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
     --tag python/instore/pmp-integration-proxy `
     --file app.base.dockerfile `
     --target app .

# Run the docker container
docker run --rm -it `
    --name pmp-integration-proxy `
    -v "$(pwd):/opt/project" `
    -p 1010:8080 surquest/app-split-balancer:latest

docker run --rm -it `
    --name pmp-integration-proxy `
    -p 1010:8080 python/instore/pmp-integration-proxy
```