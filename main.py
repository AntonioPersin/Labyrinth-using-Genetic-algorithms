from copy import copy, deepcopy
from math import *
from threading import Thread
from time import sleep
from tkinter import *
from tkinter import ttk
from tkinter.font import *
from random import *


"""
for round-robin crossing-over TOP_SELECTION_PARENTS_COUNT_ROUND_ROBIN ammount of parents is selected
this means that POP_SIZE needs to be some number that corresponds with round-robin values listed below

Parents | POP_SIZE
    3   |   6
    4   |   12
    5   |   20
    6   |   30
    7   |   42
    8   |   56
    9   |   72
    10  |   90
    11  |   110

according to the table TOP_SELECTION_PARENTS_COUNT_ROUND_ROBIN will be set automatically
"""
POP_SIZE=1
GENOME_SIZE=20


"""
SELECTION
type 1: first mistake index is used to rank parents
type 2: parents are ranked depending on first mistake index and high score index, taking into account 
        the difference between the two, importance of the difference depends on the factor chosen

CROSSING
type 1: round-robin with genome tails extending the genome itself, starting genome can be lower than 
        SHORTEST_PATH_REQ_STEPS
type 2: constant genome size round-robin, where genome is cut to GENOME_SIZE or filled up with new random genes

MUTATION
type 1: only genes in increasedMutationChance list are mutated (ones that run into a wall)
type 2: all genes can be mutated
"""
SELECTION_TYPE=2
CROSSING_TYPE=2
MUTATION_TYPE=2


"""
for SELECTION type 2 a factor is used to determine how much does difference between first mistake
and reaching the highest score matter in terms of step number
lower values (<0.5) mean more importance is given to step index when agent reached high score,
higher values (>0.5) mean more importance is given to step index when agent made their first mistake
value cannot be greater than 0.9 or lower than 0.1, increments of 0.1 are recommended values
"""
MISTAKE_TO_HS_DIFFERENCE_FACTOR=0.25


"""
genes that repeat the same mistake as the previous gene have MUTATION_MPLIER_HIGH times increased 
chance to mutate, genes that lead the agent towards the goal have MUTATION_MPLIER_LOW decreased 
chance to mutate, thus maximum PARENT_GENE_MUTATION_CHANCE is 0.25 and minimum is 0.001, 
variable is adjusted for input error
"""
#base mutation chance for first parent
PARENT_GENE_MUTATION_CHANCE_1=0.2
#base mutation chance for second parent
PARENT_GENE_MUTATION_CHANCE_2=0.2

#genes that make the agent run into a wall
MUTATION_MPLIER_HIGH=3
#genes that move the agent after first mistake
MUTATION_MPLIER_NORMAL=1
#genes that move the agent before first mistake
MUTATION_MPLIER_LOW=0.05


AGENT_COLOR="blue"
SPACE_COLOR="white"
WALL_COLOR="black"
GENES=["w", "a", "s", "d"]
GENERATION_DELAY_SECONDS=1
AGENT_ID=1


mazeStartX=3
mazeStartY=1
mazeGoalX=19
mazeGoalY=3
MAZE_WIDTH=21
MAZE_HEIGHT=21
SHORTEST_PATH_REQ_STEPS=134


mazeSimple=[
    ['X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X',],
    ['X',138,'X',999,'X',106,104,102,101,100,'X', 14, 13, 12,'X',  8,  6,  4,  3, 2,'X',],
    ['X',136,'X',133,'X',108,'X',103,'X', 99,'X', 15,'X', 11,'X','X','X',  5,'X', 1,'X',],
    ['X',134,'X',132,'X',110,'X',104,'X', 98,'X', 16,'X', 10,  9,  8,  7,  6,'X', 0,'X',],
    ['X',132,'X',131,'X',112,'X',105,'X', 97,'X', 17,'X','X','X','X','X','X','X','X','X',],
    ['X',130,'X',130,'X',114,'X',106,'X', 96,'X', 18,'X',24, 25, 26, 27, 28, 29, 30,'X',],
    ['X',128,'X',129,'X','X','X',107,'X', 95,'X', 19,'X',23,'X','X','X','X','X', 31,'X',],
    ['X',126,127,128,'X',110,109,108,'X', 94,'X', 20,21, 22,'X', 36, 35, 34, 33, 32,'X',],
    ['X',125,'X','X','X',111,'X','X','X', 93,'X', 22,'X','X','X',37,'X','X','X', 34,'X',],
    ['X',124,'X',116,114,112,'X', 90, 91, 92,'X', 24,'X', 84,'X',38,'X', 44, 40, 36,'X',],
    ['X',123,'X','X','X',113,'X', 89,'X','X','X', 26,'X', 80,'X',39,'X','X','X', 40,'X',],
    ['X',122,'X',116,115,114,'X', 88,'X', 60,'X', 28,'X', 76,'X',40, 41, 42,'X', 44,'X',],
    ['X',121,'X',117,'X','X','X', 87,'X', 56,'X', 30,'X', 72,'X','X','X',43,'X', 48,'X',],
    ['X',120,119,118,'X',82, 'X', 86,'X', 52,'X', 32,'X', 68, 64, 60,'X',44,'X', 52,'X',],
    ['X','X','X','X','X',80, 'X', 85,'X', 48,'X', 34,'X','X','X', 56,'X',45,'X', 56,'X',],
    ['X',74, 75, 76, 77, 78, 'X', 84,'X', 44, 40, 36, 40, 44, 48, 52,'X',46,'X', 60,'X',],
    ['X',73,'X','X','X', 79, 'X', 83,'X','X','X','X','X','X','X','X','X',47,'X', 64,'X',],
    ['X',72,'X', 72,'X', 80,  81, 82,'X',60, 59, 58, 57, 56,'X', 50, 49, 48,'X', 68,'X',],
    ['X',71,'X', 70,'X', 'X','X','X','X',61,'X','X','X', 55,'X', 51,'X','X','X', 72,'X',],
    ['X',70, 69, 68, 67, 66, 65, 64, 63, 62,'X', 58, 56, 54, 53, 52,'X', 84, 80, 76,'X',],
    ['X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X','X',],
]


mazeBlocks=[]
agents=[]

TOP_SELECTION_PARENTS_COUNT_ROUND_ROBIN=int((1+sqrt(1+4*POP_SIZE))/2)
if PARENT_GENE_MUTATION_CHANCE_1>0.25:
    PARENT_GENE_MUTATION_CHANCE_1=0.25
elif PARENT_GENE_MUTATION_CHANCE_1<0.001:
    PARENT_GENE_MUTATION_CHANCE_1=0.001
if PARENT_GENE_MUTATION_CHANCE_2>0.25:
    PARENT_GENE_MUTATION_CHANCE_2=0.25
elif PARENT_GENE_MUTATION_CHANCE_2<0.001:
    PARENT_GENE_MUTATION_CHANCE_2=0.001
    
STOP_AGENTS_FLAG=False


class MainWindow(Frame):
    def __init__(self, window):
        self.window = window
        self.window.title("Training area")
        super().__init__(self.window)
        self.grid(rows=MAZE_HEIGHT, columns=MAZE_WIDTH)
        self.createGUI()
        return

    def createGUI(self):
        self.window.bind("<KeyPress>", self.manualControlsListener)
        
        self.generation=(IntVar(self,1))
        popSizeLabel=Label(self,text="Population size: ")
        popSizeLabel.grid(row=int(len(mazeSimple)/4), column=len(mazeSimple[0])+1,padx=20)
        popSizeCountLabel=Label(self,text=POP_SIZE)
        popSizeCountLabel.grid(row=int(len(mazeSimple)/4), column=len(mazeSimple[0])+2,padx=20)
        genomeSizeLabel=Label(self,text="Starting genome size: ")
        genomeSizeLabel.grid(row=int(len(mazeSimple)/2), column=len(mazeSimple[0])+1,padx=20)
        genomeSizeCountLabel=Label(self,text=GENOME_SIZE)
        genomeSizeCountLabel.grid(row=int(len(mazeSimple)/2), column=len(mazeSimple[0])+2,padx=20)
        generationLabel=Label(self,text="Generation: ")
        generationLabel.grid(row=int(3*len(mazeSimple)/4), column=len(mazeSimple[0])+1,padx=20)
        generationCountLabel=Label(self,textvariable=self.generation)
        generationCountLabel.grid(row=int(3*len(mazeSimple)/4), column=len(mazeSimple[0])+2,padx=20)
        
        self.recreateMaze()
        self.createAgents()
        return
    
    def recreateMaze(self):
        for i in range(len(mazeSimple)):
            row=mazeSimple[i]
            mazeBlocks.append([])
            for j in range(len(row)):
                char=row[j]
                block=Block(self, width=4, height=2)
                
                if char=="X":
                    block.configure(bg=WALL_COLOR)
                elif char==999:
                    block.configure(bg=SPACE_COLOR, relief=SUNKEN)
                elif char==0:
                    block.configure(bg=SPACE_COLOR, relief=RIDGE)
                elif type(char)==int or char==" ":
                    block.configure(bg=SPACE_COLOR)
                
                block.score=char if type(char)==int else "!No value!"
                block.grid(row=i, column=j, padx=0, pady=0)
                mazeBlocks[i].append(block)
        return 
    
    def refreshMaze(self):
        
        for i in range(len(mazeSimple)):
            row=mazeSimple[i]
            for j in range(len(row)):
                char=row[j]
                block=mazeBlocks[i][j]
                
                if char=="X":
                    block.configure(bg=WALL_COLOR)
                elif char==999:
                    block.configure(bg=SPACE_COLOR, relief=SUNKEN)
                elif char==0:
                    block.configure(bg=SPACE_COLOR, relief=RIDGE)
                elif type(char)==int:
                    block.configure(bg=SPACE_COLOR)
                
        return 
    
    def nextGeneration(self):
        def gen():
            global STOP_AGENTS_FLAG
            print("============ GENERATION",self.generation.get(),"============")
            self.releaseAgents()
            while(not STOP_AGENTS_FLAG):
                sleep(GENERATION_DELAY_SECONDS)
                if STOP_AGENTS_FLAG:
                    break
                gen=self.generation.get()
                self.generation.set(gen+1)
                print("============ GENERATION",self.generation.get(),"============")
                self.refreshMaze()
                self.breedAgent()
                self.releaseAgents()
                self.update()
            return
        
        self.after(GENERATION_DELAY_SECONDS*1000,Thread(target=gen).start)
            
        return
    
    def manualControlsListener(self, event):
        global STOP_AGENTS_FLAG
        if event.char=="w":
            agents[POP_SIZE-1].moveUp()
        elif event.char=="a":
            agents[POP_SIZE-1].moveLeft()
        elif event.char=="s":
            agents[POP_SIZE-1].moveDown()
        elif event.char=="d":
            agents[POP_SIZE-1].moveRight()
        elif event.char=="q":
            STOP_AGENTS_FLAG=True
        return
    
    def createAgents(self):
        for i in range(POP_SIZE):
            genome=choices(GENES, k=GENOME_SIZE)
            agent=Agent(self.window,mazeStartX,mazeStartY,genome)
            agents.append(agent)
        return
    
    def breedAgent(self):
        global agents
        global STOP_AGENTS_FLAG
        if SELECTION_TYPE==1:
            parents=self.selectionFMI(TOP_SELECTION_PARENTS_COUNT_ROUND_ROBIN)
        elif SELECTION_TYPE==2:
            parents=self.selectionFactorBased(TOP_SELECTION_PARENTS_COUNT_ROUND_ROBIN)
        
        """
        for p in parents:
            p.identify()
        """
        
        agents.clear()
        if CROSSING_TYPE==1:
            agents=self.crossingOverRoundRobinExtending(parents)
        elif CROSSING_TYPE==2:
            agents=self.crossingOverRoundRobinAdjusting(parents)
        
        return
    
    def releaseAgents(self):
        for agent in agents:
            agent.walk()
        return
    
    def selectionFMI(self, winners):
        agents.sort(key=lambda x: x.firstMistakeIndex, reverse=True)
        return agents[:winners]
    
    def selectionFactorBased(self, winners):
        global agents
        def calculate_agent_score(agent):
            score=0
            difference=agent.agentHighScoreIndex-agent.firstMistakeIndex
            score=agent.firstMistakeIndex+agent.agentHighScoreIndex-MISTAKE_TO_HS_DIFFERENCE_FACTOR*difference
            #agent.identify_short()
            #print("score:",score)
            return score
        
        agents=sorted(agents, key=calculate_agent_score, reverse=True)

        return agents [:winners]
    
    def crossingOverRoundRobinExtending(self,parents):
        children=[]
        for i in range (len(parents)):
            for j in range (i+1,len(parents)):
                parent1=copy(parents[i])
                parent2=copy(parents[j])
                
                if MUTATION_TYPE==1:
                    parent1=self.mutationOnlyRedundancies
                    (parent1,PARENT_GENE_MUTATION_CHANCE_1)
                    parent2=self.mutationOnlyRedundancies
                    (parent2,PARENT_GENE_MUTATION_CHANCE_2)
                elif MUTATION_TYPE==2:
                    parent1=self.mutationAllGenes
                    (parent1,PARENT_GENE_MUTATION_CHANCE_1)
                    parent2=self.mutationAllGenes
                    (parent2,PARENT_GENE_MUTATION_CHANCE_2)
                
                if parent1.madeMistake==False:
                    genomeKid1=parent1.genome[:parent1.firstMistakeIndex+1]
                    +parent2.genome[parent2.firstMistakeIndex:]
                else:
                    genomeKid1=parent1.genome[:parent1.firstMistakeIndex]
                    +parent2.genome[parent2.firstMistakeIndex:]
                kid1=Agent(self.window,mazeStartX,mazeStartY,genomeKid1)
                
                if parent2.madeMistake==False:
                    genomeKid2=parent2.genome[:parent2.firstMistakeIndex+1]
                    +parent1.genome[parent1.firstMistakeIndex:]
                else:
                    genomeKid2=parent2.genome[:parent2.firstMistakeIndex]
                    +parent1.genome[parent1.firstMistakeIndex:]
                kid2=Agent(self.window,mazeStartX,mazeStartY,genomeKid2)
                
                children.append(kid1)
                children.append(kid2)
        return children
    
    def crossingOverRoundRobinAdjusting(self,parents):
        children=[]
        for i in range (len(parents)):
            for j in range (i+1,len(parents)):
                parent1=copy(parents[i])
                parent2=copy(parents[j])
                
                if MUTATION_TYPE==1:
                    parent1=self.mutationOnlyRedundancies(parent1,PARENT_GENE_MUTATION_CHANCE_1)
                    parent2=self.mutationOnlyRedundancies(parent2,PARENT_GENE_MUTATION_CHANCE_2)
                elif MUTATION_TYPE==2:
                    parent1=self.mutationAllGenes(parent1,PARENT_GENE_MUTATION_CHANCE_1)
                    parent2=self.mutationAllGenes(parent2,PARENT_GENE_MUTATION_CHANCE_2)
                
                if parent1.madeMistake==False:
                    genomeKid1=parent1.genome[:parent1.firstMistakeIndex+1]+parent2.genome[parent2.firstMistakeIndex:]
                else:
                    genomeKid1=parent1.genome[:parent1.firstMistakeIndex]+parent2.genome[parent2.firstMistakeIndex:]
                if len(genomeKid1)<GENOME_SIZE:
                    while len(genomeKid1)<GENOME_SIZE:
                        genomeKid1.append(choice(GENES))
                else:
                    genomeKid1=genomeKid1[:GENOME_SIZE]
                
                kid1=Agent(self.window,mazeStartX,mazeStartY,genomeKid1)
                
                if parent2.madeMistake==False:
                    genomeKid2=parent2.genome[:parent2.firstMistakeIndex+1]+parent1.genome[parent1.firstMistakeIndex:]
                else:
                    genomeKid2=parent2.genome[:parent2.firstMistakeIndex]+parent1.genome[parent1.firstMistakeIndex:]
                if len(genomeKid2)<GENOME_SIZE:
                    while len(genomeKid2)<GENOME_SIZE:
                        genomeKid2.append(choice(GENES))
                else:
                    genomeKid2=genomeKid2[:GENOME_SIZE]
                kid2=Agent(self.window,mazeStartX,mazeStartY,genomeKid2)
                
                children.append(kid1)
                children.append(kid2)
        return children
    
    def mutationOnlyRedundancies(self,agentToMutate,baseMutationChance):
        
        genesToMutate=agentToMutate.increasedMutationChance
        for mutationGene in genesToMutate:
            if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_HIGH):
                currGene=agentToMutate.genome[mutationGene]
                newGenes=list(GENES)
                newGenes.remove(currGene)
                mutatedGene=choice(newGenes)
                agentToMutate.genome[mutationGene]=mutatedGene
        
        return agentToMutate
    
    def mutationAllGenes(self,agentToMutate,baseMutationChance):
        def replace(agent,geneIndex):
            currGene=agent.genome[geneIndex]
            newGenes=list(GENES)
            newGenes.remove(currGene)
            mutatedGene=choice(newGenes)
            agent.genome[geneIndex]=mutatedGene
            return
        
        for gIndex,_ in enumerate(agentToMutate.genome):
            if gIndex<agentToMutate.firstMistakeIndex:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_LOW):
                    replace(agentToMutate,gIndex)
            elif gIndex in agentToMutate.increasedMutationChance:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_HIGH):
                    replace(agentToMutate,gIndex)
            else:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_NORMAL):
                    replace(agentToMutate,gIndex)
        
        return agentToMutate
    
"""
    nije potrebno jer se roditelji duboko kopiraju, metoda funkcionira 
    def mutationAllGenesChild(self,agentToMutate,baseMutationChance,increasedChanceList):
        def replace(agent,geneIndex):
            currGene=agent.genome[geneIndex]
            newGenes=list(GENES)
            newGenes.remove(currGene)
            mutatedGene=choice(newGenes)
            agent.genome[geneIndex]=mutatedGene
            return
        for gIndex,_ in enumerate(agentToMutate.genome):
            if gIndex<agentToMutate.firstMistakeIndex:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_LOW):
                    replace(agentToMutate,gIndex)
            elif gIndex in increasedChanceList:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_HIGH):
                    replace(agentToMutate,gIndex)
            else:
                if randint(1,1000)<=int(baseMutationChance*1000*MUTATION_MPLIER_NORMAL):
                    replace(agentToMutate,gIndex)
        
        return agentToMutate
"""
class Agent():
    def __init__(self,window,posX,posY,genome):
        global AGENT_ID
        self.id=AGENT_ID
        AGENT_ID+=1
        self.maze=window
        self.posX=posX
        self.posY=posY
        self.firstMistakeIndex=0
        self.madeMistake=False
        self.firstMistakeScore=999
        self.agentScore=999
        self.agentHighScoreIndex=0
        self.agentHighScore=999
        
        label=mazeBlocks[self.posY][self.posX]
        self.currPositionFlag=SPACE_COLOR
        label.config(bg=AGENT_COLOR)
        
        self.genome=genome
        self.increasedMutationChance=[]
        return
    
    def moveUp(self):
        oldPosition=mazeBlocks[self.posY][self.posX]
        newPosition=mazeBlocks[self.posY-1][self.posX]
        newPosFlag=newPosition["bg"]
        if newPosFlag==WALL_COLOR:
            return -1
        elif newPosFlag==SPACE_COLOR or newPosFlag==AGENT_COLOR:
            oldPosition.config(bg=self.currPositionFlag)
            self.currPositionFlag=newPosFlag
            self.posY-=1
            newPosition.configure(background=AGENT_COLOR)
            return newPosition.score
        
    def moveDown(self):
        oldPosition=mazeBlocks[self.posY][self.posX]
        newPosition=mazeBlocks[self.posY+1][self.posX]
        newPosFlag=newPosition["bg"]
        if newPosFlag==WALL_COLOR:
            return -1
        elif newPosFlag==SPACE_COLOR or newPosFlag==AGENT_COLOR:
            oldPosition.config(bg=self.currPositionFlag)
            self.currPositionFlag=newPosFlag
            self.posY+=1
            newPosition.configure(background=AGENT_COLOR)
            return newPosition.score
    
    def moveLeft(self):
        oldPosition=mazeBlocks[self.posY][self.posX]
        newPosition=mazeBlocks[self.posY][self.posX-1]
        newPosFlag=newPosition["bg"]
        if newPosFlag==WALL_COLOR:
            return -1
        elif newPosFlag==SPACE_COLOR or newPosFlag==AGENT_COLOR:
            oldPosition.config(bg=self.currPositionFlag)
            self.currPositionFlag=newPosFlag
            self.posX-=1
            newPosition.configure(background=AGENT_COLOR)
            return newPosition.score
        
    def moveRight(self):
        oldPosition=mazeBlocks[self.posY][self.posX]
        newPosition=mazeBlocks[self.posY][self.posX+1]
        newPosFlag=newPosition["bg"]
        if newPosFlag==WALL_COLOR:
            return -1
        elif newPosFlag==SPACE_COLOR or newPosFlag==AGENT_COLOR:
            oldPosition.config(bg=self.currPositionFlag)
            self.currPositionFlag=newPosFlag
            self.posX+=1
            newPosition.configure(background=AGENT_COLOR)
            return newPosition.score
        
    def walk(self):
        for stepIndex, command in enumerate(self.genome):
            if command=="w":
                newScore=self.moveUp()
            elif command=="a":
                newScore=self.moveLeft()
            elif command=="s":
                newScore=self.moveDown()
            elif command=="d":
                newScore=self.moveRight()
            
            if newScore!=-1 and newScore<self.agentScore:
                if newScore<self.agentHighScore:
                    self.agentHighScore=newScore
                    self.agentHighScoreIndex=stepIndex
                self.agentScore=newScore
            elif newScore!=-1 and newScore>=self.agentScore:
                if not self.madeMistake:
                    self.firstMistakeIndex=stepIndex
                    self.firstMistakeScore=self.agentScore
                    self.madeMistake=True
                self.agentScore=newScore
                self.increasedMutationChance.append(stepIndex)
            elif newScore==-1:
                if not self.madeMistake:
                    self.firstMistakeIndex=stepIndex
                    self.firstMistakeScore=self.agentScore
                    self.madeMistake=True
                self.increasedMutationChance.append(stepIndex)
            
            if newScore==0:
                print("END REACHED NOT OPTIMALLY")
                self.genome=self.genome[:stepIndex+1]
                if newScore==0 and len(self.genome)==SHORTEST_PATH_REQ_STEPS:
                    global STOP_AGENTS_FLAG
                    print("!!!!!!!!!!!!!!! END REACHED !!!!!!!!!!!!!!!!!")
                    self.identify()
                    STOP_AGENTS_FLAG=True
                    break
                self.increasedMutationChance=[i for i in self.increasedMutationChance if i<=SHORTEST_PATH_REQ_STEPS-1]
                break
                
        self.identify()
        #self.identify_short()
        return
    
    def identify(self):
        print("------------------- Agent",self.id,"-------------------")
        if not self.madeMistake:
            print("First wrong step:","No mistakes")
            print("First wrong step score:","No mistakes")
        else:
            print("First wrong step:",self.firstMistakeIndex+1)
            print("First wrong step score:",self.firstMistakeScore)
        print("Final score:",self.agentScore)
        print("Final high score reached on step:",self.agentHighScoreIndex+1)
        print("Final high score:",self.agentHighScore)
        print("Genome:",self.genome)
        print("Increased mutation chance indexes:",self.increasedMutationChance)
        print("======================================================")
        return
    
    def identify_short(self):
        print("This is agent",self.id)
        return
    
    def __copy__(self):
        clonedAgent=Agent(self.maze,self.posX,self.posY,list(self.genome))
        clonedAgent.firstMistakeIndex=self.firstMistakeIndex
        clonedAgent.madeMistake=self.madeMistake
        clonedAgent.firstMistakeScore=self.firstMistakeScore
        clonedAgent.agentScore=self.agentScore
        clonedAgent.agentHighScoreIndex=self.agentHighScoreIndex
        clonedAgent.agentHighScore=self.agentHighScore
        clonedAgent.increasedMutationChance=list(self.increasedMutationChance)
        return clonedAgent


class Block(Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = None
        return
        

def main():
    p = MainWindow(Tk())
    p.update()
    p.nextGeneration()
    p.mainloop()
    
    return

main()