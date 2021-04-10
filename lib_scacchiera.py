class Scacchiera(): #scrivo la mia matriciona, i nomi dei pezzi sono i nomi delle immagini da caricare
	def __init__(self):
		self.board = [
			['tn', 'cn', 'an', 'dn', 'rn', 'an', 'cn', 'tn'],
			['pn', 'pn', 'pn', 'pn', 'pn', 'pn', 'pn', 'pn'],
			['-', '-', '-', '-', '-', '-', '-', '-'],
			['-', '-', '-', '-', '-', '-', '-', '-'],
			['-', '-', '-', '-', '-', '-', '-', '-'],
			['-', '-', '-', '-', '-', '-', '-', '-'],
			['Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb'],
			['Tb', 'Cb', 'Ab', 'Db', 'Rb', 'Ab', 'Cb', 'Tb']
		]
		self.muoveilBianco = True #all'inizio muove il bianco
		self.moveLog = [] #lista delle mosse (magari mettiamo l'opzione di tornare indietro)
		self.arroccoBiancoCorto = True
		self.arroccoBiancoLungo = True
		self.arroccoNeroCorto = True
		self.arroccoNeroLungo = True
		self.varco_poss = 8 #possibilità di presa al varco, 8: non permessa, valore minore di 8 indica su quale colonna è permessa.
		self.click_in_out = []



	def controlloColoreMossa(self, mossa):
		#controlla che il pezzo mosso sia del giocatore che ha il tratto
		risposta = (not self.muoveilBianco) and mossa.pezzo_mosso[-1] == 'n'
		risposta = risposta or (self.muoveilBianco and mossa.pezzo_mosso[-1] == 'b')
		return risposta
    


	def muovere(self, mossa):
		#funzione che modifica la matriciona
		if self.controlloColoreMossa(mossa) and self.mossaValida(mossa):
			#cancello il pezzo ce lascia la casa di partenza
			#metto il pezzo sulla casa di arrivo
			#metto la mossa nello storico
			self.board[mossa.riga_inizio][mossa.colonna_inizio] = '-'
			self.board[mossa.riga_fine][mossa.colonna_fine] = mossa.pezzo_mosso
			self.moveLog.append([mossa.NotazioneBella(), mossa.NotazioneBrutta()])
			self.gestisciMossa(mossa)



	def gestisciMossa(self, mossa):
		#funzione a cui si passa il pezzo mosso e la mossa, dentro a questa funzione 
		#si possono inserire tutte le logiche complesse di ciascuna mossa.
        #NOTA: la funzione viene chiamata dopo che la mossa è stata eseguita.
       
		self.gestisciArrocco(mossa)
		#se muove il bianco mo tocca al nero e viceversa
		self.muoveilBianco = not self.muoveilBianco



	def gestisciArrocco(self, mossa):
		#dato il pezzo mosso e la sua casella determina se far perdere un arrocco.
		casa_i = [mossa.riga_inizio, mossa.colonna_inizio]
		casa_f = [mossa.riga_fine, mossa.colonna_fine]

		#Se ho mosso il re.
		if mossa.pezzo_mosso[0] == "R":
			self.arroccoBiancoCorto = False
			self.arroccoBiancoLungo = False
			#Se ho mosso il re di due allora sposto la torre come da arrocco.
			if casa_f == [7,2]:
				self.board[7][3] = self.board[7][0]
				self.board[7][0] = "-"
			if casa_f == [7,6]:
				self.board[7][5] = self.board[7][7]
				self.board[7][7] = "-"

		if mossa.pezzo_mosso[0] == "r":
			self.arroccoNeroCorto = False
			self.arroccoNeroLungo = False
			if casa_f == [0,2]:
				self.board[0][3] = self.board[0][0]
				self.board[0][0] = "-"
			if casa_f == [0,6]:
				self.board[0][5] = self.board[0][7]
				self.board[0][7] = "-"

		#Se una torre è stata mossa o catturata dalla/nella casa di partenza
		if casa_i == [7,0] or casa_f == [7,0]:
			self.arroccoBiancoLungo = False
		if casa_i == [7,7] or casa_f == [7,7]:
			self.arroccoBiancoCorto = False
		if casa_i == [0,0] or casa_f == [0,0]:
			self.arroccoNeroLungo = False
		if casa_i == [0,7] or casa_f == [0,7]:
			self.arroccoNeroCorto = False



	def calcolaControlloCasa(self, r, c):
		#Controlla se la casa è controllata da ciascun giocatore,
		# ritorna una tupla di due elementi booleani, il primo 
		# indica se il bianco ha almeno un controllo, il secondo
		#se il nero ha almeno un controllo.

		#La logica seguita è, data la casa, controllare se sono presenti
		#pedoni che possono catturare in quella casa,
		#poi se ci sono cavalli nelle otto (o meno) case da cui possono 
		#giungere, poi alfieri o donne nelle case accessibili sulla diagonale, 
		#poi torri e donne sulle traverse e infine re nelle case attorno.

		#Preferisco tenere un numero e non True e False così da includere subito
		#il numero di controlli.

		controllo_bianco = 0
		controllo_nero = 0

		#SEQUENZA PER IL BIANCO ******************
		# PEDONI -----------------
		#per fare i controlli devo escludere che sono su una delle case al bordo
		#non posso avere pedoni bianchi in prima (qui è r=7 per come funzionano le matrici)
		if not r == 7:
			if not (c == 0 or c == 7):
				controllo_bianco += self.board[r+1][c+1] == "Pb"
				controllo_bianco += self.board[r+1][c-1] == "Pb"
			elif c == 0:
				controllo_bianco += self.board[r+1][c+1] == "Pb"
			elif c == 7:
				controllo_bianco += self.board[r+1][c-1] == "Pb"

		# RE ----------------------
		for d_r in [-1,0,+1]:
			for d_c in [-1,0,+1]:
				if 0<=r+d_r<=7 and 0<=c+d_c<=7 and not d_r+d_c == 0:
					controllo_bianco += self.board[r+d_r][c+d_c] == "Rb"

		# TORRE / DONNA -----------
		#I segni mi dicono in che direzione cercare partendo dalla casella interessata, ho quattro
		#direzioni possibili, due per le righe e due per le colonne.
		#Le considero definendo i segni sign_r = +-1 e sign_c = +-1.
		for sign_r in [-1,+1]:
			for d_r in range(1,8):
				if not 0<=r+sign_r*d_r<=7:
					break
				controllo_bianco += self.board[r+sign_r*d_r][c] == "Tb" or self.board[r+sign_r*d_r][c] == "Db"
				if not self.board[r+sign_r*d_r][c] == "-":
					break
		for sign_c in [-1,+1]:
			for d_c in range(1,8):
				if not 0<=c+sign_c*d_c<=7:
					break
				controllo_bianco += self.board[r][c+sign_c*d_c] == "Tb" or self.board[r][c+sign_c*d_c] == "Db"
				if not self.board[r][c+sign_c*d_c] == "-":
					break
		
		# ALFIERE / DONNA ----------
		#Stessa logica dei segni di prima, questa volta i due for per righe e colonne sono
		#incapsulati in modo diverso perché sto trattando le diagonali (quattro direzioni).
		for sign_r in [-1, +1]:
			for sign_c in [-1, +1]:
				for d in range(1,8):
					if not (0<=r+sign_r*d<=7 and 0<=c+sign_c*d<=7):
						break
					controllo_bianco += self.board[r+sign_r*d][c+sign_c*d] == "Ab" or self.board[r+sign_r*d][c+sign_c*d] == "Db"
					if not self.board[r+sign_r*d][c+sign_c*d] == "-":
						break
		# CAVALLI -----------------
		#Guardo se in una delle otto case raggiungibili da un cavallo ho un cavallo.
		#Nota: sfrutto il fatto che il cavallo muove a elle e che le righe saltate 
		# più le colonne saltate fanno 3.
		for d_r in [-2,-1,+1,+2]:
			for d_c in [int(2/d_r), -int(2/d_r)]:
				if (0<=r+d_r<=7 and 0<=c+d_c<=7):
					controllo_bianco += self.board[r+d_r][c+d_c] == "Cb"

		#SEQUENZA PER IL NERO ******************
		# PEDONI -----------------
		#per fare i controlli devo escludere che sono su una delle case al bordo
		#non posso avere pedoni bianchi in prima (qui è r=7 per come funzionano le matrici)
		if not r == 0:
			if not (c == 0 or c == 7):
				controllo_nero += self.board[r-1][c+1] == "pn"
				controllo_nero += self.board[r-1][c-1] == "pn"
			elif c == 0:
				controllo_nero += self.board[r-1][c+1] == "pn"
			elif c == 7:
				controllo_nero += self.board[r-1][c-1] == "pn"

		# RE ----------------------
		for d_r in [-1,0,+1]:
			for d_c in [-1,0,+1]:
				if 0<=r+d_r<=7 and 0<=c+d_c<=7 and not d_r+d_c == 0:
					controllo_nero += self.board[r+d_r][c+d_c] == "rn"

		# TORRE / DONNA -----------
		#I segni mi dicono in che direzione cercare partendo dalla casella interessata, 
		#ho quattro direzioni possibili, due per le righe e due per le colonne.
		#Le considero definendo i segni sign_r = +-1 e sign_c = +-1.
		for sign_r in [-1,+1]:
			for d_r in range(1,8):
				if not 0<=r+sign_r*d_r<=7:
					break
				controllo_nero += self.board[r+sign_r*d_r][c] == "tn" or self.board[r+sign_r*d_r][c] == "dn"
				if not self.board[r+sign_r*d_r][c] == "-":
					break
		for sign_c in [-1,+1]:
			for d_c in range(1,8):
				if not 0<=c+sign_c*d_c<=7:
					break
				controllo_nero += self.board[r][c+sign_c*d_c] == "tn" or self.board[r][c+sign_c*d_c] == "dn"
				if not self.board[r][c+sign_c*d_c] == "-":
					break

		# ALFIERE / DONNA ----------
		#Stessa logica dei segni di prima, questa volta i due for per righe e colonne sono
		#incapsulati in modo diverso perché sto trattando le diagonali (quattro direzioni).
		for sign_r in [-1, +1]:
			for sign_c in [-1, +1]:
				for d in range(1,8):
					if not (0<=r+sign_r*d<=7 and 0<=c+sign_c*d<=7):
						break
					controllo_nero += self.board[r+sign_r*d][c+sign_c*d] == "an" or self.board[r+sign_r*d][c+sign_c*d] == "dn"
					if not self.board[r+sign_r*d][c+sign_c*d] == "-":
						break
		# CAVALLI -----------------
		#Guardo se in una delle otto case raggiungibili da un cavallo ho un cavallo.
		#Nota: sfrutto il fatto che il cavallo muove a elle e che le righe saltate 
		# più le colonne saltate fanno 3.
		for d_r in [-2,-1,+1,+2]:
			for d_c in [int(2/d_r), -int(2/d_r)]:
				if (0<=r+d_r<=7 and 0<=c+d_c<=7):
					controllo_nero += self.board[r+d_r][c+d_c] == "cn"

		return (controllo_bianco, controllo_nero)



	def controllaScacchi(self):
		#Determina se uno dei due giocatori è sotto scacco, ritorna una tupla (sb, sn)
		# in cui bss = True se il bianco è sotto scacco, e nss = True se lo il nero, sono ciascuno
		# a False se invece non c'è lo scacco.
		# (b/n)ss significa (bianco/nero)SottoScacco.
		bss = False
		nss = False
		for r in range(0,8):
			for c in range(0,8):
				if self.board[r][c] == "Rb":
					#il bianco è sotto scacco se il nero controlla la casa del re
					bss = bool(self.calcolaControlloCasa(r,c)[1]) 
				if self.board[r][c] == "rn":
					nss = bool(self.calcolaControlloCasa(r,c)[0])
		return (bss,nss)



	def mossaValida(self, mossa): #controllo che il pezzo selezionato possa muovere come indicato
		#Scrivo gli "if" uno dentro l'altro per comodità di lettura.
		#Per tuttu i pezzi: controlla che sulla casa di arrivo indicata non ci sia un pezzo dello stesso colore
		# "risposta" sarà il discrimante, dove viene trovata una mossa valida è impostato a True
		risposta = False 
		ri = mossa.riga_inizio
		rf = mossa.riga_fine
		ci = mossa.colonna_inizio
		cf = mossa.colonna_fine

		if not (mossa.pezzo_mosso[-1] == self.board[rf][cf][-1]):
			#  TORRE ----------------------
			#- controlla che hai dato o la stessa diagonale o la stessa traversa
			#- controlla che non ci siano pezzi in mezzo
			if mossa.pezzo_mosso[0].lower() == "t":
				if ri == rf:
					if all(elem == "-" for elem in self.board[ri][min(ci,cf)+1:max(ci,cf)]): #riga libera
						risposta = True
						
				if ci == cf:
					colonna_parz = [] #queste tre righe selezionano le case attraversate sulla riga
					for r in range(min(ri,rf)+1, max(ri,rf)):
						colonna_parz.append(self.board[r][ci])
					if all(elem == "-" for elem in colonna_parz):
						risposta = True
						
	
			# Alfiere --------------------------
			# controlla che stai muovendo in diagonale (DeltaRighe = DeltaColonne)
			# controlla che non ci siano pezzi in mezzo
			if mossa.pezzo_mosso[0].lower() == "a" and abs(cf-ci) == abs(ri-rf):
				casa_vuota = True
				dir_righe = 1 #questa e la prossima indicano la direzione dell'alfiere
				dir_colon = 1
				if ri > rf :
					dir_righe = -1
				if ci > cf :
					dir_colon = -1
				for i in range(1, abs(rf-ri)):
					if not self.board[ri + dir_righe*i][ci+dir_colon*i] == '-':
						casa_vuota = False
				if casa_vuota == True:
					risposta = True
					
			# Cavallo ----------------------------
			# Controlla che muova a elle, DeltaRighe*DeltaColonne == 2
			if (mossa.pezzo_mosso[0].lower() == "c") and abs((cf-ci)*(ri-rf)) == 2:
				risposta = True
				
			# Donna ------------------------------
			# Come torre o alfiere
			if mossa.pezzo_mosso[0].lower() == "d":
				if ri == rf: #stessa riga
					#riga libera
					if all(elem == "-" for elem in self.board[ri][min(ci,cf)+1:max(ci,cf)]):
						risposta = True
						
				if ci == cf: #stessa colonna
					colonna_parz = [] #queste tre righe selezionano le case attraversate sulla riga
					for r in range(min(ri,rf)+1, max(ri,rf)):
						colonna_parz.append(self.board[r][ci])
					if all(elem == "-" for elem in colonna_parz):
						risposta = True
						
				if abs(cf-ci) == abs(ri-rf): #in diagonale
					casa_vuota = True
					dir_righe = 1 #questa e la prossima indicano la direzione della donna
					dir_colon = 1
					if ri > rf :
						dir_righe = -1
					if ci > cf :
						dir_colon = -1
					for i in range(1, abs(rf-ri)):
						if not self.board[ri + dir_righe*i][ci+dir_colon*i] == '-':
							casa_vuota = False
					if casa_vuota == True:
						risposta = True
						
			# Re -----------------------------------
			# Come torre o alfiere ma di una sola casella
			if mossa.pezzo_mosso[0].lower() == "r":
				print("Sto muovendo il re")
				if (abs(ci-cf) <= 1 and abs(ri-rf) <= 1):
					risposta = True
				# Mossa di arrocco
				# bianco
				if ri == 7 and rf == 7 and ci == 4:
					via_libera_lunga = self.board[7][3] == "-" and self.board[7][1] == "-" and not (self.calcolaControlloCasa(rf,6)[1] or self.calcolaControlloCasa(rf,5)[1] or self.calcolaControlloCasa(rf,4)[1])
					via_libera_corta = not (self.calcolaControlloCasa(rf,2)[1] or self.calcolaControlloCasa(rf,3)[1] or self.calcolaControlloCasa(rf,4)[1])
					if cf == 6 and self.arroccoBiancoCorto and via_libera_corta:
						risposta = True
					if cf == 2 and self.arroccoBiancoLungo and via_libera_lunga:
						risposta = True
				# nero
				if ri == 0 and rf == 0 and ci == 4:
					via_libera_lunga = self.board[rf][3] == "-" and self.board[rf][1] == "-" and not (self.calcolaControlloCasa(rf,6)[0] or self.calcolaControlloCasa(rf,5)[0] or self.calcolaControlloCasa(rf,6)[0]) 
					via_libera_corta = not (self.calcolaControlloCasa(rf,2)[0] or self.calcolaControlloCasa(rf,3)[0] or self.calcolaControlloCasa(rf,6)[0])
					if cf == 6 and self.arroccoNeroCorto and via_libera_corta:
						risposta = True
					if cf == 2 and self.arroccoNeroLungo and via_libera_lunga:
						risposta = True
					
					

			# PEDONE -------------------------
			# se muovi sulla riga successiva controlla che sia vuota (riga precedente per nero)
			# se muovi di uno in diagonale controlla che ci sia un pezzo avversario oppure che 
			# puoi effettuare la presa al varco.
			if mossa.pezzo_mosso[0] == "p" or mossa.pezzo_mosso[0] == "P":
				#spinta di uno
				if ci-cf == 0 and (rf-ri) == 1 and self.board[rf][cf] == '-' and not self.muoveilBianco:
					risposta = True
				if ci-cf == 0 and (rf-ri) == -1 and self.board[rf][cf] == '-' and self.muoveilBianco:
					risposta = True
				#cattura in diagonale
				if (ci-cf)**2 == 1 and (rf-ri) == 1 and not self.board[rf][cf][-1] == '-' and not self.muoveilBianco:
					risposta = True
				if (ci-cf)**2 == 1 and (rf-ri) == -1 and not self.board[rf][cf][-1] == '-' and self.muoveilBianco:
					risposta = True
				# al varco
				if (ci-cf)**2 == 1 and (rf-ri) == 1 and not self.muoveilBianco and ri == 4 and cf == self.varco_poss:
					self.board[ri][cf] = "-"
					risposta = True		
				if (ci-cf)**2 == 1 and (rf-ri) == -1 and self.muoveilBianco and ri == 3 and cf == self.varco_poss:
					self.board[ri][cf] = "-"
					risposta = True

			# Spegni la presa al varco, metto qui tale riga perché è immediatamente dopo le mosse di uno pedone.
			self. varco_poss = 8 # 8: non permessa
					
			# Pedone, spinta di due, è importante che sia alla fine così da segnare la possibilità di
			# presa al varco dopo aver controllato tutto il resto	
			if mossa.pezzo_mosso[0] == "p" or mossa.pezzo_mosso[0] == "P":
				#spinta di due, segna anche su quale colonna è possibile prendere en passant
				if ci-cf == 0 and (rf-ri) == 2 and ri == 1 and self.board[rf][cf] == '-' and not self.muoveilBianco:
					self.varco_poss = ci
					risposta = True
				if ci-cf == 0 and (rf-ri) == -2 and ri == 6 and self.board[rf][cf] == '-' and self.muoveilBianco:
					self.varco_poss = ci
					risposta = True
		return risposta



	def stampaControlloCase(self):
		#Stampo due scacchiere separate per bianco e nero con segnati i numeri di controlli per ciascuna casella.
		print("Controlli bianchi \t Controlli neri")
		for r in range(0,8):
			#Riga del bianco
			for c in range(0,8):
				print("{} ".format(self.calcolaControlloCasa(r,c)[0]), end= "")
			
			print("\t", end="")
			#Riga del nero
			for c in range(0,8):
				print("{} ".format(self.calcolaControlloCasa(r,c)[1]), end= "")
			print("\n",end="")
		print("\n", end="")






class Mossa():
    numeri = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    numeriback = {v: k for k, v in numeri.items()}
    lettere = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    lettereback = {v: k for k, v in lettere.items()}

    def __init__(self, inizio, fine, board):
        self.riga_inizio = inizio[0]
        self.colonna_inizio = inizio[1]
        self.riga_fine = fine[0]
        self.colonna_fine = fine[1]
        self.pezzo_mosso = board[self.riga_inizio][self.colonna_inizio] #memorizzo il pezzo che si deve muovere
        self.pezzo_catturato = board[self.riga_fine][self.colonna_fine] #memorizzo un eventuale pezzo da levare

    def NotazioneBrutta(self):
        return self.RigheColonne(self.riga_inizio, self.colonna_inizio) + self.RigheColonne(self.riga_fine, self.colonna_fine)

    def RigheColonne(self, r, c):
        return self.lettereback[c] + self.numeriback[r]#passo da notazione matrice a notazione algebrica
    
    def NotazioneBella(self):
    	ritorno = self.RigheColonne(self.riga_fine, self.colonna_fine)
    	if not self.pezzo_mosso[0].upper() == "P":
    		ritorno = self.pezzo_mosso[0].upper() + ritorno
    	return ritorno
