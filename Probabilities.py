# # Function updating probabilities of genes to be selected
def calculProbabilities(weights):
	probabilities = []
	for i in weights: probabilities.append(i * (1 / sum(weights)))
	return probabilities
