from pathfinder import PathFinder

graph={'Start':{'A':1,'C':1},'A':{'B':1},'C':{'B':1},'B':{'Goal':1},'Goal':{}}
finder=PathFinder(graph)
print(finder.find_multiple_paths('Start','Goal',3))
