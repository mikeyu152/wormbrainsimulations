import csv

def tallyCSV(filename):
	with open(filename, 'r') as csvfile:
		totalDict = {}
		reader = csv.reader(csvfile)
		keys = None
		currAlpha = None
		currThreshold = None
		for line in reader:
			if keys == None:
				keys = line
			elif line[0] == 'alpha':
				totalDict[line[1]] = {}
				currAlpha = line[1]
			elif line[0] == 'threshold':
				totalDict[currAlpha][line[1]] = {}
				currThreshold = line[1]
			else:
				for elem in line:
					if elem in totalDict[currAlpha][currThreshold]:
						totalDict[currAlpha][currThreshold][elem] += 1
					else:
						totalDict[currAlpha][currThreshold][elem] = 1
		return totalDict

def parseDict(totalDict):
	with open('noiseinterpreted.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for alpha in totalDict:
			for threshold in totalDict[alpha]:
				writer.writerow(['alpha', str(alpha), 'threshold', str(threshold)])
				row1 = []
				row2 = []
				for key in totalDict[alpha][threshold]:
					row1.append(key)
					row2.append(totalDict[alpha][threshold][key]*.001)
				writer.writerow(row1)
				writer.writerow(row2)

def tallyCSV2(filename):
	with open(filename, 'r') as csvfile:
		totalDict = {}
		reader = csv.reader(csvfile)
		keys = None
		currAlpha = None
		currThreshold = None
		for line in reader:
			if keys == None:
				keys = line
				for key in keys:
					totalDict[key] = {}
			elif line[0] == 'alpha':
				currAlpha = line[1]
			elif line[0] == 'threshold':
				currThreshold = line[1]
			else:
				for elem in line:
					if currThreshold not in totalDict[elem]:
						totalDict[elem][currThreshold] = {}
					if currAlpha not in totalDict[elem][currThreshold]:
						totalDict[elem][currThreshold][currAlpha] = 1
					else:
						totalDict[elem][currThreshold][currAlpha] += 1
						
		return totalDict

def parseDict2(totalDict):
	with open('noiseinterpretedunfreezetiny.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		for elem in totalDict:
			for threshold in totalDict[elem]:
				row = ['elem', str(elem), 'threshold', str(threshold), '']
				for alpha in range(25):
					alpha = str(alpha)
					if alpha not in totalDict[elem][threshold]:
						totalDict[elem][threshold][alpha] = 0
					row.append(totalDict[elem][threshold][alpha]*.001)
				writer.writerow(row)


totalDict = tallyCSV2('noisesimsunfrozensmaller.csv')
print 'done tallying'
parseDict2(totalDict)
 