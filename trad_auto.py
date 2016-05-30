# -*- coding: utf-8 -*-
# fichier Bicorpus.py
from __future__ import division
import codecs
import random
import numpy.random as np
import numpy as npy
import os
import subprocess, shlex
import matplotlib.pyplot as plt

# Stocke une liste de BiPhrase
# Le constructeur s'occupe de lire les fichiers et créer les BiPhrases.
class BiCorpus:
	""" parcours deux fichiers """
	def __init__(self, srcFileName, cibFileName, limit = -1):
		self.bip = list() # liste de Biphrase
		sFile = codecs.open(srcFileName, "rt") #fichier source (fr)
		cFile = codecs.open(cibFileName, "rt") #fichier cible (en)
		# on prend des phrases = lignes
		self.sPhrase = sFile.readline().strip().split()
		self.cPhrase = cFile.readline().strip().split()
		self.compteur = 0
		## print "ligne" + str(compteur+1)
		## print "{0} : {1}\n".format(sPhrase, cPhrase)

		""" on met ces phrases ensemble dans la liste bip """
		""" et verification du nombre de ligne """
		while self.sPhrase and self.cPhrase:
			self.compteur += 1
			self.bip.append(BiPhrase(self.sPhrase, self.cPhrase))
			if(self.compteur == limit):
				break
			self.sPhrase = sFile.readline().strip().split()
			self.cPhrase = cFile.readline().strip().split()
			## print "ligne" + str(compteur+1)
			## print "{0} : {1}\n".format(sPhrase, cPhrase)
		#print "Le BiCorpus contient "+str(compteur)+" BiPhrases"

		""" associer l'alignement à biphrase """
		"""for biph in self.bip:
			alis = biph.align # récupérer l'alignement
			#print "alignement : " + str(alis)"""

	""" fonc evaluation alignement """ 
	def eval_align(self):
		""" créer notre fichier txt """
		self.fiche = open("notre_align.txt", "w") # écrire en écrasant la dernière version
		self.nb_ph = 0

		for biph in self.bip:
			self.nb_ph = self.nb_ph + 1 # indice pour le nombre de phrase
			self.alis = biph.nouv_align # récupérer l'alignement
			#print "après aligné : " + str(alis)

			for i in range(len(self.alis)):
				# si le mot anglais est aligné avec un mot français
				# = si il est pas -1
				if(self.alis[i] != -1):
					#print self.nb_ph,i,alis[i]
					self.fiche.write(str(self.nb_ph) +" "+ str(i+1) +" "+ str(self.alis[i]+1) +"\n")
				# si le mot anglais n'est pas aligné (=-1), affiche rien
				
		self.fiche.close()

		""" obtenir AER (taux d'erreur d'alignement) """
		# ligne de commande pour exécuter évaluation
		#command_line = 'perl '+'aa_eval_align.pl '+'reference_alignments.txt '+'notre_align.txt'
		command_line = 'perl aa_eval_align.pl reference_alignments.txt notre_align.txt'
		args = shlex.split(command_line)
		# récupérer le résultat
		p1, err = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
		# split les élements avec espace puis prend le dernier = partie AER
		aer = p1.splitlines()[-1]
		# récupérer seule valeur
		aer = aer.split(" ")[-1]
		#print aer
		return aer


class BiPhrase:
	"""
	Le constructeur prend en paramètres les deux phrases (source et cible).
	source et cible sont des listes de str. 
	"""
	def __init__ (self, source, cible):
		self.align = list()
		self.nouv_align = list() # pour le nouvel alignement
		self.src = source
		self.cib = cible
		idmax = len(self.cib)-1
		for i in range(len(self.src)):
			self.align.append(random.randint(-1,idmax))
			self.nouv_align.append(0)


class Compte:
	"""
	dictionnaire de mot français et le compte.
	on récupère l'alignement de mot anglais, et récupère le mot français.
	Ensuite on compte l'apparision de chaque mot français.
	"""
	def __init__(self):
		self.fr_com = dict()
		# tous les comptes associés à un mot ang = nbr d'apparrition de ce mot ang
		self.nbr_cpts = 0

	def getCompte(self, mof):
		if mof in self.fr_com:
			return self.fr_com[mof]
		# sinon ou dnas tous les cas ?
		else:
			return 0

	def com_inc(self, mof):
		# si il y a déjà le mot français dans le dico, alors on ajoute 1 à ce mot
		if mof in self.fr_com:
			self.fr_com[mof] = self.fr_com[mof] + 1
			self.nbr_cpts = self.nbr_cpts + 1
			#return self.fr_com
		# sinon ajouter 1 pour ce mot
		else:
			self.fr_com[mof] = 1
			self.nbr_cpts = self.nbr_cpts + 1 

	# pour faire un nouvel alignement dans l'echantillon, 
	# il faut d'abord couper l'ancien alignement = enlever 1 pour cet alignement
	def com_dec(self, mof):
		# si il existe ce mot dans le dico (et il est plus 0), alors enlève 1
		if mof in self.fr_com and self.fr_com[mof] > 0:
			self.fr_com[mof] = self.fr_com[mof] - 1
			self.nbr_cpts = self.nbr_cpts - 1
		# sinon ?? => rien


""" un mot clé anglais, et on appelle la classe compte """
class Cooccurrence:
	def __init__(self, alpha):
		self.en_comptes = dict() # dictionnaire d'objets Compte
		self.en_com = dict() # pour échantillon
		self.alp = alpha
		self.nbr_e = 0 # nombre de mot_e
		self.probas = [1,1,1]

	""" mot_en et le compte """
	def setCooc(self, bicorpus):
		for bc in bicorpus.bip:			
			for i in range(len(bc.align)):
				m_f = bc.src[i]
				m_e = "NULL" # par défaut on met rien
				al = bc.align[i]

				# mot ang est aligné à un mot fr quand alignement n'est pas -1
				if al != -1:
					m_e = bc.cib[al]
				# appel cooc_inc() pour cette combinaison des mots
				self.cooc_inc(m_f, m_e)
				#print "rés",self.en_comptes[m_e].getCompte(m_f)





	def cooc_inc(self, mf, me):
		# si il existe ce mot ang dans la dico, appel com_inc de la classe Compte
		# et récupère le mot fr et son compte
		if me in self.en_comptes:
			if me != -1:
				self.nbr_e += 1

			compt = self.en_comptes[me] # objet Compte()
			#print "inc: before",me,mf,compt.getCompte(mf)
			compt.com_inc(mf)
			#print "inc: after",me,mf,compt.getCompte(mf)
			# stocker le compte récupéré !
			self.en_comptes[me] = compt

		# sinon créer un objet Compte pour ce mot ang et appel com_inc 
		# (pour ajouter 1 pour ce compte) et récupère le mot fr et son compte
		else:
			if me != -1:
				self.nbr_e += 1

			compt = Compte()
			#print "inc0 :before",me,mf,compt.getCompte(mf)
			compt.com_inc(mf)
			#print "inc0: after",me,mf,compt.getCompte(mf)
			self.en_comptes[me] = compt


	def cooc_dec(self, mf, me):
		# si il existe ce mot ang dans la dico, appel com_dec
		# (pour enlever 1 pour ce compte) et récupère le mot fr et son compte
		if me in self.en_comptes:
			if me != -1:
				self.nbr_e -= 1
			compt = self.en_comptes[me]
			#print "dec: before",me,mf,compt.getCompte(mf)
			compt.com_dec(mf)
			#print "dec: after",me,mf,compt.getCompte(mf)
			self.en_comptes[me] = compt
		# sinon => rien


	""" renouveler alignement => améliorer la performance """
	def echantillon(self, bicorpus):
		for bc in range(len(bicorpus.bip)):
		#for bc in bicorpus.bip:
			b = bicorpus.bip[bc]
			for i in range(len(b.src)):
				""" décrémenter le compte fr, ang qui sont alignés """
				mf = b.src[i]
				me = "NULL"
				al = b.align[i]
				#print "before",mf,al
				if al != -1:
					me = b.cib[al]
				self.cooc_dec(mf, me)

				# créer la liste de probabilité pour chaque mot_fr
				self.probas = list()
				# initialiser
				self.probas.append(self.probabilite(mf, "NULL"))
				for e in b.cib:
					# on ajoute la probabilité calculée dans la liste
					self.probas.append(self.probabilite(mf, e))
				#print self.probas

				""" calculer la probas base en 1 et trouver le nouvel alignement """
				# normaliser la probabilité de chaque mot_fr
				#print "avant : "+str(self.probas)
				self.probas = self.normaliser(self.probas)
				#print "apres : "+str(self.probas)

				# obtenir le nouvel alignement pour ce mot_fr
				self.nouv_alis = (np.multinomial(1, self.probas).argmax())-1
				#print "nouv align : "+str(self.nouv_align)

				""" renouveler l'alignement et le compe de cette nouvelle combinaison """
				b.nouv_align[i] = self.nouv_alis
				#print bc.nouv_align
				#print "modifié : "+str(bc.nouv_align[i])
				nouv_al = self.nouv_alis
				#print "after",nouv_al
				if nouv_al != -1:
					nouv_me = b.cib[nouv_al]
				else:
					nouv_me = "NULL"
				#print nouv_me
				self.cooc_inc(mf, nouv_me)


	def probabilite(self, motf, mote):
		""" récupérer les deux comptes d'apparition """
		if mote in self.en_comptes:
			compt = self.en_comptes[mote]
			cef = compt.getCompte(motf) #nbr d'apparition de cette combinaison de mots 
			#print "cef:",cef, "ce",ce
			ce  = compt.nbr_cpts #nbr d'apparition le mot anglais qui est aligné
			#ce = self.nbr_e
			#print mote,"ce",ce
			taille = len(compt.fr_com)

			""" calculer la proba """ 
			# il faut multiplier la taille de dico fr
			a = cef + self.alp
			#print "long:",len(compt.fr_com)
			#print "cef + self.alp",a
			#print self.alp*len(compt.fr_com)
			b = ce + (self.alp*taille)
			#print "ce + (self.alp*len(compt.fr_com))",b
			prob = a / b
			#prob = (cef + self.alp) / (ce + (self.alp*len(compt.fr_com)))

			return prob

		# si ce mot ang n'est pas aligné, on retourne un petit chiffre
		else: 
			return 1/100000000	


	def normaliser(self, pr):
		#print pr

		self.somme = 0
		# on calcule la somme de la list Probas
		for p in range(len(pr)):
			self.somme = self.somme + pr[p]
		# diviser chaque élément par la somme pour faire en sorte que la somme est égal à 1
		for i in range(len(pr)):
			pr[i] = pr[i] / self.somme
		return pr



if __name__ == "__main__":
	""" initialisation des élements """
	itera = 50 # nbr itération pour ensemble
	alpha = 0.000001 # pour calculer la probabilité
	limit = 447 # nbr lignes de phrase
	list_aer = list() # liste de valeur AER pour plot
	list_iter = list() # liste de l'itération, pour passer en npy.array

	""" initialiser fonctions """
	bico = BiCorpus("./train.fr", "./train.en", limit)
	cooc = Cooccurrence(alpha)
	#cooc.setCooc(bico)
	#bico.eval_align()
	#pr = list()
	#pr = [1,1,1]
	#cooc.normaliser(pr)

	""" itération """
	for i in range(itera):

		#print i,"er:",cooc.echantillon(bico)
		cooc.echantillon(bico)
		aers = bico.eval_align()
		#print aers
		#bico.eval_align()
		list_aer.append(aers)
		print list_aer
		list_iter.append(i+1)

	""" #afficher en plot """
	x = npy.array(list_iter)
	y = npy.array(list_aer)
	#print "list_aer", list_aer

	plt.plot(x,y)
	#plt.xlabel('nbr itération')
	#plt.ylabel('valeur AER')
	plt.title('Evolution de AER')
	plt.grid(True)
	plt.show()
