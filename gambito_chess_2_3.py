import pygame as py
import lib_scacchiera

py.init()

lato_finestra = 600
larghezza = 512
altezza = 512
traverse = 8
lato_casa = altezza // traverse
immagine = {}
bordo = (lato_finestra-altezza)//2
	
def caricalo(): #per ogni pezzo nella matrice associo un'immagine da caricare
    pezzi = ['Tb', 'Cb', 'Ab', 'Db', 'Rb', 'Pb', 'tn', 'cn', 'an', 'dn', 'rn', 'pn']
    for pezzo in pezzi:
        immagine[pezzo] = py.transform.scale(py.image.load('./immagini/' + pezzo + '.png'), (lato_casa, lato_casa))

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

def main():
	screen = py.display.set_mode((lato_finestra, lato_finestra)) #crea una finestra
	clock = py.time.Clock() #l'orologio serve ad aggiornare la finestra
	screen.fill(py.Color('black')) #metto uno sfondo bianco
	gs = lib_scacchiera.Scacchiera() #gs = game state
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
					move = lib_scacchiera.Mossa(gs.click_in_out[0], gs.click_in_out[1], gs.board)
					gs.muovere(move)
					selezione_casa = () #setto tutto a zero
					gs.click_in_out = []

					#Blocco per il debug o stampe di test:
					print("Mossa immessa: " +move.NotazioneBella())
					gs.stampaControlloCase()
					print("bss, nss = {}".format(gs.controllaScacchi()))
					print("\n")

		#Blocco di stampa dell'immagine
		stampaPosizione(screen, gs)
		stampaTurno(screen, gs.muoveilBianco)
		clock.tick(10) #dico quante volte aggiorno lo schermo al secondo (ho messo un numero a caso)
		py.display.flip() #aggiorno lo schermo


if __name__ == '__main__':
    main() #faccio girare il codice del main
