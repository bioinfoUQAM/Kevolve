# IMPORT
import Gene
import Data
import numpy
import K_mers
import Weight
import Matrix
import Model
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

# GENERATE DATA
k_min = 3
k_max = 7
print("Loading data")
data = Data.generateData("Input/data.fasta", "Input/target.csv")
print("Generating K-mers")
K_mers = K_mers.generate_K_mers(data, k_min, k_max)
print("Number of features :", len(K_mers))
X, y = Matrix.generateMatrice(data, K_mers, k_min, k_max)
X = Preprocessing.minMaxScaling(X)
X = numpy.matrix(X)

# INITIALIZE VIARIABLES
n_features = numpy.size(X, 1)
n_iterations = 250
n_results = 50
n_chromosomes = 100
n_genes = 100
crossover_rate = 0.2
mutation_rate = 1 / n_genes
objective = False
objective_score = 0.40

# MAIN
results = []
temporaryPopulation = []
genes = Gene.generateGenes(n_features)
weights = Weight.initialWeights(genes)
probabilities = Probabilities.calculProbabilities(weights)

# PREPROCESSING
# VarianceThreshold or other filter method

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
	
	scores = Fitness.fitnessCalculation(X, y, population)
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

# GET INDEXES AND K-MERS 
Indexes = []
Selected_k_mers = []
for r in results:
	index = []
	for i in r: 
		if K_mers[i] not in Selected_k_mers: 
			Selected_k_mers.append(K_mers[i])
			index.append(Selected_k_mers.index(K_mers[i]))
		else: index.append(Selected_k_mers.index(K_mers[i]))
	Indexes.append(index)

# SAVE INDEXES
f = open("Output/Model/indexes.csv", "w")
for i in Indexes:
	for j in i: f.write(str(j) + ",")
	f.write("\n")

f.close()

# SAVE K-MERS
f = open("Output/Model/k_mers.csv", "w")
for k_mer in Selected_k_mers: 
	f.write(k_mer + "\n");
f.close()

# BUILT AND SAVE MODEL
X, y = Matrix.generateMatrice(data, Selected_k_mers, k_min, k_max)
X = Preprocessing.minMaxScaling(X)
X = numpy.matrix(X)
Model.fit(X, y, Indexes)


Model.predict("Output", "Input/data.fasta", "Input/target.csv")


# IDEA Si model chargé ==== > prédiction d'un fichier test  ou pred + eva si 3 csv données
# AJouter les variables path et model path au début pour les condition 
# Ajouter info sur le chargement exemple matrice en cosntruction
