





def main():
	wordlist = []

	#just change filename to extract firstnames instead
	with open('lastnames_extra.txt', 'r') as f:
		wordlist = [line.split(None, 1)[0] for line in f]

	#just change filename to extract firstnames instead
	with open('lastnames.txt', 'w') as f:
		for word in wordlist:
			f.write(word + '\n')






if __name__ == "__main__":
	main()