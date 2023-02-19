# Heuristic based approaches for the ESTP with solid and soft obstacles

`Thesis data - ESTP with obstacles.xlsx` contains the results obtained by GA, PBSA and PPA. 

Note: The results reported are the best of out 20 runs.


### Euclidean Steiner Tree with Obstacles
This repo contains the implementation for the ESTP with obstacles using three different algorithms: Genetic Algorithm, Plant Propagation Algorithm, and Population-based Simulated Annealing.

The project structure is as follows:

```

├── ga/
│   ├── index.py
│   ├── src/
│   │   ├── chromosome.py
│   │   ├── chromosome_one.py
│   │   ├── chromosome_three.py
│   │   ├── chromosome_two.py
│   │   ├── collision.py
│   │   ├── delaunay.py
│   │   ├── mst.py
│   │   ├── obstacle.py
│   │   ├── plot.py
│   │   ├── population.py
│   │   ├── reader.py
├── ppa/
│   ├── index.py
│   ├── src/ (similar to GA)
├── pbsa/
│   ├── index.py
│   ├── src/ (similar to GA)

```
### File Descriptions

* chromosome_one.py, chromosome_two.py, and chromosome_three.py: Implementations of different types of chromosomes used in the the algorithms.
* collision.py: Implementation to check collisions between edges and obstacles.
* delaunay.py: Implementation of Delaunay triangulation and calculating centroids.
* fermat.py: Implementation to calculate Fermat-Torricelli point.
* mst.py: Implementation of the minimum spanning tree algorithm using Kruskal's algorithm.
* obstacle.py: Implementation of the class that represents an obstacle.
* plot.py: Implementation to visualize different trees, chromosomes, etc.
* population.py: Implementation of the population class that contains crossover, mutations etc.
* reader.py: Code to read in input dataset.
* ga/: Code specific to the GA implementation.
* ppa/: Code specific to the PPA implementation.
* sa/: Code specific to the PBSA implementation.
* index.py: The entry point for each of the three algorithms.


