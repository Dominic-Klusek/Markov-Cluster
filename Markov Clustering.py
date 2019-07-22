#Dominic Klusek
#CSC 769 Markov Clustering
import numpy as np
from time import sleep
import pandas as pd

def inflate(m_2, inflation_factor):
	'''
		Function to inflate the matrix
		Input:
			m_2 np.array
		Output:
			inflated np.array
	'''
    #create copy of m_2 and square each value individually
	inflated = np.array(m_2, copy=True)**inflation_factor
    
    #normalize columns
	inflated, sum = normalize_columns(inflated)
	
    #threshold smaller values
	inflated[inflated < 10**-7] = 0.0
	
    #return inflated matrix and column sums
	return inflated, sum

def normalize_columns(array):
    '''
        Function to normalize the columns of the matrix
        Input:
            array: numpy array
        Output:
            copy: numpy array of normalized matrix
            sums: list containing sums of columns
    '''
    #create copy of array
	copy = np.array(array, copy=True)
	# get sums of each column for development of markov chain
	sum = []
	for y in range(copy.shape[0]):
		temp = 0
		for x in range(copy.shape[1]):
			temp += copy[x,y]
		sum.append(temp)

    #normalize each column
	for y in range(copy.shape[0]):
		for x in range(copy.shape[1]):
			copy[x,y] = copy[x,y] / sum[y]
		
	return copy, sum



#main
#open file as f
with open('GraphConnections.txt', 'rt') as f:
    #create excel file
	writer = pd.ExcelWriter("MarkovMatrix.xlsx", engine="xlsxwriter")
	
	#read the number of nodes in the graph from the first line fo the file
	numberOfNodes = int(f.readline().replace("\n", ""))
    
    #create datasetructures based on number of nodes
	m1 = np.zeros((numberOfNodes,numberOfNodes))
	previousM1 = np.zeros((numberOfNodes,numberOfNodes))
	m2 = np.zeros((numberOfNodes,numberOfNodes))
	m3 = np.ones((numberOfNodes,numberOfNodes))

	#read each line and create the weight matrix
	for line in f.readlines():
		numbersList = [int(num) for num in line.replace("\n","").split(" ")]
		m1[numbersList[0],[numbersList[1]]] = numbersList[2]
		m1[numbersList[1],[numbersList[0]]] = numbersList[2]

    #write original weight matrix to excel file
	pd.DataFrame(data=m1, index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Original", startrow=0)
	
	
	#add self loops
	for i in range(m1.shape[1]):
		m1[i,i] = 1

#write weight matrix with self-loops to excel file
	pd.DataFrame(data=m1, index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Original", startrow=numberOfNodes+2)
	
	#create markov matrix
	m1, sums = normalize_columns(m1)

    #write original markov matrix to excel file
	pd.DataFrame(data=m1, index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Original", startrow=numberOfNodes*2+4)

	epsilon = 10**-7
	iteration = 0
    #while convergence is not achieved perform loop
	while(np.sum(m3) > epsilon):
		print("Iteration: ", iteration)
		iteration+=1

		#store previous m1 to compare to inflated one
		previousM1 = np.array(m1, copy=True)
		
		#square m1
		m2 = np.linalg.matrix_power(m1, 2)
		
		counter = 0

		#inflate squared m1
		m1, columnSums = inflate(m2, 2)

		#find difference between arrays
		m3 = np.sum(np.abs(m1 - m2)) / (numberOfNodes**2)
		
		#write M_1, M_2, columns sums, and M_3 to excel page Iteration n
		pd.DataFrame(data=np.round(m2, 4), index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Iteration "+str(iteration), startrow=0)
		pd.DataFrame(data=np.round(columnSums, 4), index=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Iteration "+str(iteration), startrow=numberOfNodes+2)
		pd.DataFrame(data=np.round(m1, 4), index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Iteration "+str(iteration), startrow=numberOfNodes*2+4)
		pd.DataFrame(data=np.round(np.abs(m1 - previousM1), 4), index=np.arange(0,numberOfNodes), columns=np.arange(0,numberOfNodes)).to_excel(writer, sheet_name="Iteration "+str(iteration), startrow=numberOfNodes*3+6)

	#save excel file
	writer.save()
