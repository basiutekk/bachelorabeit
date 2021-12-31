
def writeresult(graph,result,solution1 , solution2, solution3):
    result_name = "result_"+str(result)
    f = open("./result/"+result_name, "a")
    f.write(str(graph)+" & " + str(solution1)+" & " + str(solution2)+" & " + str(solution3)+"//"+"\n")
    f.close()
def readfile(result):
    f = open("./result/compare_results.txt")
    lines = f.readlines()
    for line in lines[1:]:
        splitted = line.split(":")
        graph = splitted[0]
        sol1 = splitted[3]
        sol2 = splitted[4]
        sol3 = splitted[5]
        writeresult(graph,result,sol1,sol2,sol3)

if __name__ == '__main__':
    readfile(6)