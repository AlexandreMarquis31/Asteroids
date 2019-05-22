"""on importe tous les modules necessaires aux bon déroulement du jeu"""
import random,pickle,platform,sys
print(sys.path)
from tkinter import *
from math import *                      
from datetime import datetime
from tkinter import font
LARGEUR = 500
HAUTEUR = 650


if platform.system() == "Darwin" :
    from PIL import Image, ImageTk
    def chargerImage(path):   ## corrige le problem des pngs transparents sur Mac
        img =Image.open(path)
        alpha = img.split()[-1]  # Pull off the alpha layer
        ab = alpha.tobytes()  # Original 8-bit alpha
        checked = []  # Create a new array to store the cleaned up alpha layer bytes
        # Walk through all pixels and set them either to 0 for transparent or 255 for opaque fancy pants
        transparent = 50  # change to suit your tolerance for what is and is not transparent
        p = 0
        for pixel in range(0, len(ab)):
            if ab[pixel] < transparent:
                checked.append(0)  # Transparent
            else:
                checked.append(255)  # Opaque
            p += 1
        mask = Image.frombytes('L', img.size, bytes(checked))
        img.putalpha(mask)
        newIm= ImageTk.PhotoImage(img)
        return newIm
    
else :
    def chargerImage(path):
        img= PhotoImage(file=path)
        return img


def animervaisseau(): ##anime le vaisseau après avoir recu des dégats
    """ici on fait un test pour repérer l'image du vaisseau et on lui attribue l'image inverse"""
    if invincible == True:
        if Canevas.itemcget(vaisseau,'image') == str(joueur):
           Canevas.itemconfigure(vaisseau, image=joueurInverse)
        else:
            Canevas.itemconfigure(vaisseau, image=joueur)
        Mafenetre.after(200,animervaisseau)

def animerBoss():
    """ici on fait un test pour repérer l'image du boss et on lui attribue l'image inverse"""
    global boss
    if boss != None and animBoss== True:
        if Canevas.itemcget(boss,'image') == str(ennemi):
            Canevas.itemconfigure(boss, image=ennemiInverse)
        else:
            Canevas.itemconfigure(boss, image=ennemi)
        Mafenetre.after(200,lambda: animerBoss())
        
def deplacerBoss(deplacement):
    """deplace le boss horizontalement et change de sens lorsqu'il rencontre un mur"""
    global boss
    if stopJeu==False and boss!=None:
        if Canevas.coords(boss)[0]+asteroid.width()*(0.5)>LARGEUR+1 or Canevas.coords(boss)[0]-asteroid.width()*(0.5)<-1 :
            deplacement=-deplacement                           
        Canevas.move(boss,deplacement,0)
        Mafenetre.after(15,lambda: deplacerBoss(deplacement))
        
def ajouterTypeEnnemi ():
    """increment le nombre de types d'enemi et fait apparaitre un boss"""
    global nombreTypeEnnemi, boss
    nombreTypeEnnemi+=1
    boss = Canevas.create_image((LARGEUR/2)-25,asteroid.height(),image=ennemi,tag="bossastero5")
    lancerTirennemi(boss)
    Mafenetre.after(15,lambda: deplacerBoss(vitesse/1.5))

def afficherScores():
    """créer une fenetre avec les scores"""
    fenetreScores = Tk()
    fenetreScores.resizable(width=False, height=False)
    fenetreScores.title("Scores")
    fenetreScores.geometry("240x"+str(int(HAUTEUR/2)+50)+"+"+str(int((fenetreScores.winfo_screenwidth()/2)-77))+"+"+str(int(HAUTEUR/2)))
    canvas1=Canvas(fenetreScores)
    canvas = Canvas(canvas1,height=280,width=220)
    frame = Frame(canvas,width=220,height=280)
    frame.grid_columnconfigure(0,minsize=73)
    frame.grid_columnconfigure(1,minsize=73)
    frame.grid_columnconfigure(2,minsize=73)
    vsb = Scrollbar(canvas1, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right",fill="y")
    canvas.pack(side="left",fill="both")
    canvas1.grid(row=2,columnspan=3)
    canvas.create_window((0,0),window=frame, anchor="n")
    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    Label(fenetreScores, text="Score\n").grid(row=1, column=1)
    Label(fenetreScores, text="Nom\n").grid(row=1, column=2)
    Label(fenetreScores, text="Meilleurs scores",font="-weight bold").grid(row=0, columnspan=3,column=0)
    Label(fenetreScores, text="Rang\n").grid(row=1, column=0)
    Button(fenetreScores,text="Rejouer" , command=lambda: game(fenetreScores)).grid(row=3, column=0,columnspan=3)
    for i in range (len(scores)):
        Label(frame, text=str(scores[i])).grid(row=i, column=2)
        Label(frame, text=noms[i]).grid(row=i, column=1)
        Label(frame, text=str(i+1)).grid(row=i, column=0)

def sauvegarderNom():       ##sauvegarde le nom et le score
    global noms, scores
    with open("scores.txt",'rb') as fichier:
        scores= pickle.load(fichier)
    with open("noms.txt",'rb') as fichier:
        noms= pickle.load(fichier)
    scores.append(int(Canevas.itemcget(CompteurScore, 'text')))
    while len(noms) < len(scores)-1:
        noms.append("Inconnu")
    noms.append(entree.get())
    while sorted(scores, reverse=True) != scores:
        for e in range (len(scores)-1):
            if scores[e]<scores[e+1]:
                attente= scores[e]
                scores[e]=scores[e+1]
                scores[e+1] = attente
                attente= noms[e]
                noms[e]=noms[e+1]
                noms[e+1] = attente
    with open("noms.txt",'wb') as fichier:
        pickle.dump(noms, fichier)
    with open("scores.txt",'wb') as fichier:
        pickle.dump(scores, fichier)
    fenetreNom.destroy()
    Mafenetre.destroy()
    afficherScores()
    
def sauvegarder(): ##creer une fenetre demandant d'entrer un nom
    global entree, fenetreNom
    fenetreNom = Tk()
    fenetreNom.resizable(width=FALSE, height=FALSE)
    fenetreNom.title("Nom")
    label0 = Label(fenetreNom, text="Game Over!", fg="red")
    label0.grid(row=0, column=0)
    scoreLabel = Label(fenetreNom, text="Score: "+ Canevas.itemcget(CompteurScore, 'text'))
    scoreLabel.grid(row=1, column=0)
    asteroLabel = Label(fenetreNom, text="Astéroïdes détruits: "+ str(StatsAsteros))
    asteroLabel.grid(row=2, column=0)
    metresLabel = Label(fenetreNom, text="Distance parcourue: "+str(int(((vitesse*10)-(HAUTEUR/10)))/10)+" km")
    metresLabel.grid(row=3, column=0)
    precisionLabel = Label(fenetreNom, text="Precision: "+ str(int((StatsAsteros/max(1,StatsTirs))*100))+"%")
    precisionLabel.grid(row=4, column=0)
    label = Label(fenetreNom, text="Entrez votre nom: ")
    label.grid(row=5, column=0)
    entree = Entry(fenetreNom)
    entree.grid(row=6, column=0)
    bouton=Button(fenetreNom,text="Sauvegarder" , command=sauvegarderNom)
    bouton.grid(row=7, column=0)
    fenetreNom.geometry("174x190+"+str(int((fenetreNom.winfo_screenwidth()/2)-77))+"+"+str(int(HAUTEUR/2)))
    
def game(fenetre=Tk()): ##Lance le jeu
    global tirInfini,bonus,bonus2,invincible,CompteurScore,debris,ennemiInverse,nombreMun,nombreVies,asteroid2, asteroid1,coeur, asteroid0,Canevas,vaisseau,vitesse,Mafenetre,stopJeu,StatsTirs,StatsAsteros,asteroid,joueur,joueurInverse,maintenant,ennemi,animBoss,boss, nombreTypeEnnemi, nombreVies
    fenetre.destroy()
    Mafenetre = Tk()
    joueur=chargerImage('joueur.png')
    joueurInverse=chargerImage('joueurInverse.png')
    ennemiInverse=chargerImage('ennemiInverse.png')
    asteroid= chargerImage('asteroid.png')
    asteroid2= chargerImage('asteroid2.png')
    asteroid1= chargerImage('asteroid1.png')
    asteroid0= chargerImage('asteroid0.png')
    ennemi= chargerImage('ennemi.png')
    debris=chargerImage('debris.png')
    bonus=chargerImage('Bonus.png')
    bonus2=chargerImage('Bonus 1.png')
    coeur=chargerImage('coeur.PNG')
    Mafenetre.resizable(width=False, height=False)
    Font = font.Font(family='Helvetica', size=int(HAUTEUR/30))
    Mafenetre.geometry(str(LARGEUR)+"x"+str(HAUTEUR)+"+"+str(int((Mafenetre.winfo_screenwidth()/2)-(LARGEUR/2)))+"+0")
    Mafenetre.title("Asteroïdes")
    Canevas = Canvas(Mafenetre,height=HAUTEUR,width=LARGEUR, bg='black',highlightthickness=0)
    Canevas.pack()
    Canevas.focus_set()
    Canevas.bind('<Key>',GestionTouches)
    EntrainDeRecharger=stopJeu=animBoss=invincible=tirInfini=False
    nombreMun =0
    rechargerMun(50)
    CompteurScore = Canevas.create_text(10,5+(HAUTEUR/30),text='0', font= Font, fill='white', width= LARGEUR, anchor= 'w')
    nombreVies=3
    Canevas.create_image(5+(coeur.width()/2),HAUTEUR-(coeur.height()/2)-5,image=coeur, tag="vie")
    Canevas.create_image(5+(coeur.width()/2),HAUTEUR-(coeur.height()/2)-10-coeur.width(),image=coeur, tag="vie")
    Canevas.create_image(5+(coeur.width()/2),HAUTEUR-(coeur.height()/2)-15-2*coeur.width(),image=coeur, tag="vie")
    vaisseau =Canevas.create_image(joueur.width()/2,HAUTEUR-(joueur.height()/2)-5,image=joueur, tag="vaisseau")
    Canevas.tag_lower(vaisseau)
    vitesse = HAUTEUR/100
    StatsAsteros = StatsTirs =nombreTypeEnnemi=0
    boss=None
    lancerennemi()
    augmenterScore()
    Mafenetre.focus_force()
    maintenant=datetime.now()
    Mafenetre.after(20000, lambda: ajouterTypeEnnemi())
    cielEtoile()
    
def cielEtoile():
    if stopJeu==False:
        emplacement= random.randint(0,LARGEUR)
        etoile = Canevas.create_rectangle(emplacement,-2,emplacement+3,-5,fill="white",tag="etoile")
        Canevas.tag_lower(etoile)
        Canevas.tag_lower(etoile)
        Mafenetre.after(15,lambda: deplacerObjet(etoile,vitesse))
    Mafenetre.after(60,cielEtoile)

def lancerTirennemi (ennemi):
    if len(Canevas.coords(ennemi))> 0:
        tir = Canevas.create_rectangle(Canevas.coords(ennemi )[0]-1.5,Canevas.coords(ennemi)[1]+(joueur.height()/2)+(HAUTEUR/40),Canevas.coords(ennemi)[0]+1.5,Canevas.coords(ennemi)[1]+(joueur.height()/2),fill='yellow',width=0, tag="tirennemi")
        Mafenetre.after(30,lambda: deplacerObjet(tir,vitesse*1.5))
        Mafenetre.after(500,lambda: lancerTirennemi(ennemi))
        
def lancerennemi():
    if stopJeu==False and boss==None:
        bonusEnnemi= random.randint(0,100)
        k= random.randint(0,floor((LARGEUR/asteroid.width())-1))
        if (bonusEnnemi < 1):
            astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=bonus2,tag="bonusCoeur")
        elif (bonusEnnemi < 2):
            astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=bonus,tag="bonusTir")
        else:
            typeennemi= random.randint(0,nombreTypeEnnemi)
            if typeennemi == 0:
                astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=asteroid,tag="astero0")
            elif typeennemi == 1:
                astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=asteroid,tag="astero3")
            elif typeennemi == 2:
                astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=debris,tag="asteroIncassable")
            else:
                astero = Canevas.create_image(asteroid.width()*(k+0.5),-asteroid.height(),image=ennemi,tag="astero0")
                lancerTirennemi(astero)
        Canevas.tag_lower(astero)
        Mafenetre.after(15,lambda: deplacerObjet(astero,vitesse/1.4))
    Mafenetre.after(int(3500/vitesse),lancerennemi)

def deplacerObjet(objet,deplacement):
    global invincible,stopJeu,StatsAsteros,animBoss,boss,nombreVies,tirInfini
    if stopJeu==False and len(Canevas.coords(objet))> 0:
        Canevas.move(objet,0,deplacement)
        if Canevas.coords(objet)[1]> HAUTEUR+asteroid.height() or Canevas.coords(objet)[1] < -75:   ##Efface les asteroids ou tirs sortis de l'ecran 
            Canevas.delete(objet)
        else :
            for id in Canevas.find_overlapping(*Canevas.bbox(objet)):   ##gere les collisions
                if 'astero'  in Canevas.itemcget(id, "tag")  and "tir" in Canevas.itemcget(objet, "tag"):
                    StatsAsteros+=1
                    if Canevas.itemcget(id, "tag")[-1:]in ["1","2","3","4","5","6","7","8","9"]:
                        if 'boss' in Canevas.itemcget(id, "tag"):
                            Canevas.itemconfigure(id, tag="bossastero"+str(int(Canevas.itemcget(id, "tag")[-1:])-1))
                            if animBoss == False:
                                animBoss=True
                                animerBoss()
                                Mafenetre.after(3000, stopAnimBoss)
                        else:
                            Canevas.itemconfigure(id, tag="astero"+str(int(Canevas.itemcget(id, "tag")[-1:])-1))
                            Canevas.itemconfigure(id, image=eval("asteroid"+str(Canevas.itemcget(id, "tag")[-1:])))
                            Canevas.itemconfigure(CompteurScore, text=str(int(Canevas.itemcget(CompteurScore, 'text'))+10))
                    if Canevas.itemcget(id, "tag")[-1:] == "0" :
                        if 'boss' in Canevas.itemcget(id, "tag"):
                            Mafenetre.after(20000,lambda: ajouterTypeEnnemi() )
                            Canevas.delete(id)
                            boss=None
                            Canevas.itemconfigure(CompteurScore, text=str(int(Canevas.itemcget(CompteurScore, 'text'))+200))
                        else:
                            if Canevas.itemcget(objet, "tag") == "tir":
                                Canevas.delete(id)
                                Canevas.itemconfigure(CompteurScore, text=str(int(Canevas.itemcget(CompteurScore, 'text'))+20))            
                    Canevas.delete(objet)
                if Canevas.itemcget(id, "tag")== 'vaisseau' and Canevas.itemcget(objet, "tag")!= 'etoile':
                    if  Canevas.itemcget(objet, "tag")== 'bonusCoeur' :
                        Canevas.delete(objet)
                        Canevas.create_image(5+(coeur.width()/2),HAUTEUR-(coeur.height()/2)-((nombreVies+1)*5)-nombreVies*coeur.width(),image=coeur, tag="vie")
                        nombreVies+=1
                    elif  Canevas.itemcget(objet, "tag")== 'bonusTir' :
                        Canevas.delete(objet)
                        tirInfini=True
                        Mafenetre.after(10000,lambda: stopTirInfini() )
                    elif invincible == False :
                        for id in Canevas.find_overlapping(5,HAUTEUR-5-((nombreVies-1)*(5+coeur.width())),5+coeur.width(),HAUTEUR-5-1.5*coeur.width()-((nombreVies-1)*(5+coeur.width()))):
                            if Canevas.itemcget(id, "tag")== 'vie':
                                Canevas.delete(id)
                                nombreVies-=1
                        if nombreVies == 0:
                            stopJeu=YES
                            Canevas.unbind('<Key>')
                            sauvegarder()
                        else:
                            invincible = True
                            animervaisseau()
                            Mafenetre.after(2000,stopInvincibility)
        Mafenetre.after(15,lambda: deplacerObjet(objet,deplacement))

def stopTirInfini():
    global tirInfini
    tirInfini=False
def stopAnimBoss():
    global animBoss
    animBoss=False
    Canevas.itemconfigure(boss, image=ennemi)

def GestionTouches(event):
    global EntrainDeRecharger, stopJeu, maintenant, nombreMun, StatsTirs, pauseScore
    if stopJeu==False:
        if event.keysym == 'Return':
            stopJeu=True
            pauseScore= int(Canevas.itemcget(CompteurScore, "text"))
            Canevas.itemconfigure(CompteurScore, text="Pause")
        if event.keysym == 'Control_R' or event.keysym == 'R' or event.keysym == 'r' :
            if EntrainDeRecharger ==False and nombreMun != 50:
                rechargerMun(50)
        if (event.keysym=='d' or event.keysym=='D' or event.keysym=='Right') and Canevas.coords(vaisseau)[0]+asteroid.width()*(1.5)<LARGEUR+1:
            Canevas.move(vaisseau,asteroid.width(),0)
        if (event.keysym == 'q' or event.keysym=='Q' or event.keysym=='Left') and Canevas.coords(vaisseau)[0]-asteroid.width()*(1.5)>-1:
            Canevas.move(vaisseau,-asteroid.width(),0)
        if event.keysym == 'space':
            if nombreMun !=0 and EntrainDeRecharger== False and ((datetime.now()-maintenant).microseconds)>75000:
                tir = Canevas.create_rectangle(Canevas.coords(vaisseau)[0]-1.5,Canevas.coords(vaisseau)[1]-(joueur.height()/2)-(HAUTEUR/40),Canevas.coords(vaisseau)[0]+1.5,Canevas.coords(vaisseau)[1]-(joueur.height()/2),fill='yellow',width=0, tag="tir")
                Mafenetre.after(30,lambda: deplacerObjet(tir,-vitesse*1.5))
                StatsTirs+=1
                if tirInfini==False:
                    for id in Canevas.find_overlapping(LARGEUR-15,HAUTEUR-4-((nombreMun-1)*3),LARGEUR-5,HAUTEUR-3-((nombreMun-1)*3)):   ##gere les collisions entre astroid et tir
                        if Canevas.itemcget(id, "tag")== 'munition':
                            Canevas.delete(id)
                            nombreMun-=1
                maintenant = datetime.now()
    else:
        if event.keysym == 'Return':
            stopJeu=False
            Canevas.itemconfigure(CompteurScore, text=str(pauseScore))
            Mafenetre.after(2000,stopInvincibility)
            for id in Canevas.find_overlapping(0,0,LARGEUR,HAUTEUR):   ##   redémarre tous les asteroids et tous les tirs
                    if 'astero' in Canevas.itemcget(id, "tag"):
                        if 'boss' in Canevas.itemcget(id, "tag"):
                            deplacerBoss(vitesse/1.5)
                        else:
                            deplacerObjet(id,vitesse/1.5)
                    if 'bonus' in Canevas.itemcget(id, "tag"):
                            deplacerObjet(id,vitesse/1.5)
                    if Canevas.itemcget(id, "tag")== 'tir':
                        deplacerObjet(id,-vitesse*1.5)
                    if Canevas.itemcget(id, "tag")== 'tirennemi':
                        deplacerObjet(id,vitesse*1.5)
                    if Canevas.itemcget(id, "tag")== 'etoile':
                        deplacerObjet(id,vitesse)
            if EntrainDeRecharger ==True:
                rechargerMun(50-nombreMun)
                
def rajouterMun(nombre):
    global nombreMun, EntrainDeRecharger
    if stopJeu == False:
        Canevas.create_rectangle(LARGEUR-15,HAUTEUR-4-(nombreMun*3),LARGEUR-5,HAUTEUR-3-(nombreMun*3),fill='yellow',width=0, tag="munition")
        nombreMun+=1
        if nombreMun == nombre :
            EntrainDeRecharger= False
    
def rechargerMun(number):
    global EntrainDeRecharger
    EntrainDeRecharger=True
    for i in range(nombreMun,number):
        if stopJeu == False :
            Mafenetre.after(100*i,lambda: rajouterMun(number))

def stopInvincibility():
    global invincible
    if stopJeu == False:
        invincible=False
        Canevas.itemconfigure(vaisseau, image=joueur)
    
def augmenterScore():
    global vitesse
    if stopJeu==False:
        Canevas.itemconfigure(CompteurScore, text=str(int(Canevas.itemcget(CompteurScore, 'text'))+10))
        vitesse+=0.04
    Mafenetre.after(1000,augmenterScore)

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

game()
Mafenetre.mainloop()
