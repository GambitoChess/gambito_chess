import pygame as py

py.init()

lato_finestra = 600
larghezza = 512
altezza = 512
traverse = 8
lato_casa = altezza // traverse
immagine = {}
bordo = (lato_finestra-altezza)//2


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
		risposta = not self.muoveilBianco and mossa.pezzo_mosso[-1] == 'n'
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



	def gestisciArrocco(self, mossa):
		#dato il pezzo mosso e la sua casella determina se far perdere un arrocco
		casa_i = [mossa.riga_inizio, mossa.colonna_inizio]
		casa_f = [mossa.riga_fine, mossa.colonna_fine]

		#Se ho mosso il re
		if casa_i == [7,4]:
			self.arroccoBiancoCorto = False
			self.arroccoBiancoLungo = False
		if casa_i == [0,4]:
			self.arroccoNeroCorto = False
			self.arroccoNeroLungo = False

		#Se una torre è stata mossa o catturata dalla/nella casa di partenza
		if casa_i == [7,0] or casa_f == [7,0]:
			self.arroccoBiancoLungo = False
		if casa_i == [7,7] or casa_f == [7,7]:
			self.arroccoBiancoCorto = False
		if casa_i == [0,0] or casa_f == [0,0]:
			self.arroccoNeroLungo = False
		if casa_i == [0,7] or casa_f == [0,7]:
			self.arroccoNeroCorto = False



	def gestisciMossa(self, mossa):
		#funzione a cui si passa il pezzo mosso e la mossa, dentro a questa funzione 
		#si possono inserire tutte le logiche complesse di ciascuna mossa.
        #NOTA: la funzione viene chiamata dopo che la mossa è stata eseguita.
       
		self.gestisciArrocco(mossa)
		#se muove il bianco mo tocca al nero e viceversa
		self.muoveilBianco = not self.muoveilBianco



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
			if mossa.pezzo_mosso[0].lower() == "r" and (abs(ci-cf) == 1 or abs(ri-rf) == 1):
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
					
			# Spegni la presa al varco
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





class Mossa():
    #dizionari
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
	
def caricalo(): #per ogni pezzo nella matrice associo un'immagine da caricare
    pezzi = ['Tb', 'Cb', 'Ab', 'Db', 'Rb', 'Pb', 'tn', 'cn', 'an', 'dn', 'rn', 'pn']
    for pezzo in pezzi:
        immagine[pezzo] = py.transform.scale(py.image.load('./immagini/' + pezzo + '.png'), (lato_casa, lato_casa))
# il path delle immagini mi ha fatto dannare, se serve cambialo


def main():
	screen = py.display.set_mode((lato_finestra, lato_finestra)) #crea una finestra
	clock = py.time.Clock() #l'orologio serve ad aggiornare la finestra
	screen.fill(py.Color('black')) #metto uno sfondo bianco
	gs = Scacchiera() #gs = game state
	caricalo() #carico le immagini prima di entrare nel ciclo while, così da avere la posizione di partenza
	running = True #uso una variabile perchè scrivere 'while True' è da boomer
	selezione_casa = () #quando l'utente clicca una casa, metto la x e la y della casa qui dentro
	
	while running:
		for event in py.event.get(): #crea una lista di eventi possibili (e.g. click del mouse)
			if event.type == py.QUIT: #se l'evento è 'chiudi la finestra' esco dal ciclo while
				running = False
			if event.type == py.MOUSEBUTTONDOWN: #se l'utente clicca il mouse
				coor_mouse = py.mouse.get_pos() #prende la posizione in x e in y del cursore
				colonna = (coor_mouse[0]-bordo )// lato_casa #la x (componente 0) è associata alla colonna
				riga = (coor_mouse[1]-bordo) // lato_casa #la y (componente 1) è associata alla riga
				if 0<=colonna<8 and 0<=riga<8:
					if selezione_casa == (riga, colonna): #se l'utente clicca 2 volte la stessa casa
						selezione_casa = () #setto tutto a zero
						gs.click_in_out = []
					else:
						selezione_casa = (riga, colonna) #registro la x e la y della casa cliccata
						gs.click_in_out.append(selezione_casa) #faccio lo stesso anche qui dentro

				if len(gs.click_in_out) == 2: #se l'utente clicca la seconda casa
					#Invio della mossa cliccata all'oggetto scacchiera
					move = Mossa(gs.click_in_out[0], gs.click_in_out[1], gs.board)
					gs.muovere(move)
					selezione_casa = () #setto tutto a zero
					gs.click_in_out = []

					#Blocco stampe per i debug:
					print(move.NotazioneBrutta() + ", "+move.NotazioneBella())
					gs.stampaControlloCase()

		#Blocco stampa dell'immagine
		stampaPosizione(screen, gs)
		stampaTurno(screen, gs.muoveilBianco)
		clock.tick(10) #dico quante volte aggiorno lo schermo al secondo (ho messo un numero a caso)
		py.display.flip() #aggiorno lo schermo

def stampaPosizione(screen, gs):
	stampaScacchiera(screen)
	stampaPezzi(screen, gs.board)
	if len(gs.click_in_out) == 1:
		py.draw.rect(screen, (0, 0, 0), py.Rect(bordo+(gs.click_in_out[0][1]+0.25)*lato_casa, bordo+(0.92+gs.click_in_out[0][0])*lato_casa, lato_casa*0.5, 2))
	
def stampaTurno(screen, turnoBianco):
	latox = 30
	latoy = 10
	margine = 1
	py.draw.rect(screen, (255, 255, 255), py.Rect (bordo, bordo-20, latox, latoy))
	if not turnoBianco:
		py.draw.rect(screen, (0, 0, 0), py.Rect (bordo+margine, bordo-20+margine, latox-2*margine, latoy-2*margine))
		
def stampaScacchiera(screen): #colora le case della scacchiera
    colori = [py.Color('white'), py.Color('light blue')]
    for r in range(traverse):
        for c in range(traverse):
            colore = colori[(r+c) % 2] #se somma di riga e colonna è pari la casa è chiara, altrimenti è scura
            py.draw.rect(screen, colore, py.Rect(bordo + c * lato_casa, bordo + r * lato_casa, lato_casa, lato_casa))

	
def stampaPezzi(screen, board): #carica le immagini per ogni pezzo
    for r in range(traverse):
        for c in range(traverse):
            pezzo = board[r][c]
            if pezzo != '-':
                screen.blit(immagine[pezzo], py.Rect(bordo + c * lato_casa, bordo + r * lato_casa, lato_casa, lato_casa))

if __name__ == '__main__':
    main() #faccio girare il codice del main
