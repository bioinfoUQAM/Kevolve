###############
### IMPORTS ###
###############
import os.path
from os import makedirs

import Gene
import Data
import numpy
import Model
import K_mers
import Weight
import Matrix
import Fitness
import operator
import Solution
import Mutation
import Objective
import Selection
import Crossover
import Population
import statistics
import Probabilities
import Preprocessing

############
### CORE ###
############

# Function to extract feature subsets
def extraction(params):
 
    training_fasta = params["training_fasta"]
    training_csv = params["training_csv"]
    k_min = params["k_min"]
    k_max = params["k_max"]
    model_path = params["model_path"]

    outdir = os.path.join(model_path, "Model")
    path_pkl = os.path.join(outdir,"pkl")
    makedirs(outdir, mode=0o700, exist_ok=True)
    makedirs(path_pkl, mode=0o700, exist_ok=True)

    # GENERATE TRAINING DATA
    print("Loading data...")
    data = Data.generateTrainData(training_fasta, training_csv)
    print("Generating K-mers...")
    k_mers = K_mers.generate_K_mers(data, k_min, k_max)
    print("Number of features :", len(k_mers))
    print("Generating matrices...")
    X, y = Matrix.generateMatrice(data, k_mers, k_min, k_max)
    X = Preprocessing.minMaxScaling(X)
    X = numpy.matrix(X)

    # PREPROCESSING
    X, k_mers = Preprocessing.varianceThreshold(X, k_mers, threshold=params["var_threshold"])
    print("Number of features after preprocessing :", len(k_mers))

    # INITIALIZE VARIABLES
    n_features = numpy.size(X, 1)
    n_iterations = params["n_iterations"]
    n_results = params["n_results"]
    n_chromosomes = params["n_chromosomes"]
    n_genes = params["n_genes"]
    crossover_rate = params["crossover_rate"]
    mutation_rate = 1 / n_genes
    objective = params["objective"]
    objective_score = params["objective_score"]
        
    cv_n = params["cv_n"]
    cv_shuffle = params["cv_shuffle"]
    cv_n_jobs = params["cv_n_jobs"]

    # MAIN
    results = []
    temporaryPopulation = []
    genes = Gene.generateGenes(n_features)
    weights = Weight.initialWeights(genes)
    probabilities = Probabilities.calculProbabilities(weights)

    # EVOLUTION
    for n in range(n_iterations):
        print("\nIteration", n + 1)

        if n == 0: 
            population = Population.generateInitialPopulation(n_chromosomes, genes, n_genes, probabilities)
            print("Size of the population", len(population))
        else:
            population = Population.generateNextPopulation(n_chromosomes, genes, n_genes, probabilities)
            population = Population.mergePopulation(population, temporaryPopulation)
            print("Size of the population", len(population))
	
        scores = Fitness.fitnessCalculation(X, y, population, 
                cv_n=cv_n , cv_shuffle=cv_shuffle, cv_n_jobs=cv_n_jobs)
        print("Mean weighted score", round(statistics.mean([i[0] for i in scores]), 3), 
                "Max weighted score", round(max([i[0] for i in scores]), 3), 
                "Mean macro score", round(statistics.mean([i[1] for i in scores]), 3), 
                "Max macro score", round(max([i[1] for i in scores]), 3))

        solutions = Solution.checkSolutions(population, scores, objective_score)
        print("Number of Solutions", len(solutions))

        results = Solution.saveSolutions(results, solutions)
        print("Number of Results", len(results))

        if objective ==  False: objective = Objective.checkObjective(objective_score, scores)
        print("Objective :", objective)
	
        if objective ==  False: 
            n_genes = n_genes + 1
            mutation_rate = 1 / n_genes
        print("Number of genes :", n_genes)

        selection = Selection.selection(scores, population)
        print("Number of selection", len(selection))

        weights = Weight.updateWeights(weights, selection)
        print("Update weights")

        probabilities = Probabilities.calculProbabilities(weights)
        print("Update probabilities")

        selection = Crossover.crossover(selection, crossover_rate)
        print("Apply crossovers")

        selection = Mutation.mutation(selection, mutation_rate, genes, objective)
        print("Apply mutation")

        temporaryPopulation.clear()
        temporaryPopulation = selection

        if n_results <= len(results): break

    print("Number of results =", len(results))
	
    print("\nSave results...")	

    # GET INDEXES AND K-MERS 
    Indexes = []
    Selected_k_mers = []
    for r in results:
        index = []
        for i in r: 
            if k_mers[i] not in Selected_k_mers: 
                Selected_k_mers.append(k_mers[i])
                index.append(Selected_k_mers.index(k_mers[i]))
            else: index.append(Selected_k_mers.index(k_mers[i]))
        Indexes.append(index)

    # SAVE INDEXES
    f = open(outdir+"/indexes.csv", "w")
    for i in Indexes:
        for j in i: f.write(str(j) + ",")
        f.write("\n")

    f.close()

    # SAVE K-MERS
    f = open(outdir+"/k_mers.csv", "w")
    for k_mer in Selected_k_mers: 
        f.write(k_mer + "\n");
    f.close()
	
    # BUILT AND SAVE MODEL
    print("Save model...")
    X, y = Matrix.generateMatrice(data, Selected_k_mers, k_min, k_max)
    X = Preprocessing.minMaxScaling(X)
    X = numpy.matrix(X)
    Model.fit(X, y, Indexes, path_pkl)
