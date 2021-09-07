from qiskit import *
import numpy as np



#Function that converts the QASM format into a list that would make interpreting more convenient

def plot_counts(qc,shots=3000):
    assert qc.num_clbits > 0, "There are no classical bits to measure."
    sim = Aer.get_backend('qasm_simulator')
    counts = execute(qc,sim,shots=shots).result().get_counts()
    return plot_histogram(counts)

def get_unitary(circ):
    sim = Aer.get_backend('unitary_simulator')
    U = execute(circ,sim).result().get_unitary()
    return U


def file_to_str(filename):
    return open(filename,'r').read()

def qasm_list(string):
    string = string.replace("\n", "")
    return string.split(";")

#Function that turns formats and filters the instructions 
def instruction_gen(string):
    
    inst_set = string.split(" ")

    if "rx" in inst_set[0] or "ry" in inst_set[0] or "rz" in inst_set[0]:
        gate = inst_set[0][0:2]
        angle = inst_set[0].replace(gate+"(","")
        angle = angle.replace(")","")
        angle = angle.replace("pi","3.14159265")
        target = inst_set[1].replace("q[","")
        target = [float(eval(angle))]+[int(i) for i in target.replace("]","").split(",")] 
    
    elif "measure" in inst_set[0]:
        gate = "measure"
        target = string.replace('measure q[',"")
        target = target.replace("] -> c["," ") 
        target = [[int(i)] for i in target.replace("]","").split(" ")]

    else:
        gate = inst_set[0]
        target = inst_set[1].replace("q[","")
        target = [int(i) for i in target.replace("]","").split(",")]
    return [gate,target]

#Function that creates circuits

def make_circuit(string):
    words = string
    n_qb = 0
    n_cb = 0  
    qb = [w for w in words if w.startswith('qreg')][0]
    qb = qb.replace("qreg q[","")
    n_qb = int(qb.replace("]","")) 
    if [w for w in words if w.startswith('creg')] != []:
        cb = [w for w in words if w.startswith('creg')][0]
        cb = cb.replace("creg c[","")
        n_cb = int(cb.replace("]","")) 
    if n_cb == 0:
        qc = QuantumCircuit(n_qb)
    if n_cb != 0:
        qc = QuantumCircuit(n_qb, n_cb)
    return qc

#The main show: Implements all the functions defined before and creates a qiskit QuantumCircuit object, equivalent to the input qasm string

def interpreter(qasm_in):    
    def add_instructions(qasm_str):
        allowed_gates = ('x','y','z','rx','ry','rz','h','s','sdg','t','tdg','cx','ccx','swap','cswap','measure')
        for i in range(len(qasm_str)):
            if qasm_str[i].startswith(allowed_gates):
                gate,target = instruction_gen(qasm_str[i])
                getattr(qc, gate)(*target)
                
    if ".qasm" in qasm_in:
        qasm_str = file_to_str(qasm_in)
    else:
        qasm_str = qasm_in

    qasm = qasm_list(qasm_str)
    qc = make_circuit(qasm)
    add_instructions(qasm)
    return qc

#Gets dagger of circuit 

def get_dg(qc):
    
    if type(qc) == str:
        qc = interpreter(qc)
        u_dg = get_unitary(qc).conjugate().transpose()
        qc_dg = QuantumCircuit(qc.num_qubits)
        qc_dg.unitary(u_dg,[i for i in range(qc.num_qubits)],"qc_dg")
    if type(qc) == qiskit.circuit.quantumcircuit.QuantumCircuit:
        u_dg = get_unitary(qc).conjugate().transpose()
        qc_dg = QuantumCircuit(qc.num_qubits)
        qc_dg.unitary(u_dg,[i for i in range(qc.num_qubits)],"qc_dg")
    return qc_dg