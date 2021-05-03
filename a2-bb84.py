from qiskit import QuantumCircuit, Aer, assemble
from numpy.random import randint
import sys

class Alice:

    def __init__(self, num_bits):
        self.final_key = []
        self.num_bits = num_bits
        self.bits = randint(2, size=num_bits)
        self.bases = randint(2, size=num_bits)

    def send_message(self):
        message = []
        for i in range(self.num_bits):
            qc = QuantumCircuit(1, 1)
            if self.bases[i] == 0:  # Prepare qubit in Z-basis
                if self.bits[i] == 0:
                    pass
                else:
                    qc.x(0)
            else:  # Prepare qubit in X-basis
                if self.bits[i] == 0:
                    qc.h(0)
                else:
                    qc.x(0)
                    qc.h(0)
            qc.barrier()
            message.append(qc)
        return message

    def declare_bases(self):
        return self.bases

    def gen_final_key(self, b_bases):
        self.final_key = []
        for q in range(self.num_bits):
            if self.bases[q] == b_bases[q]:
                self.final_key.append(self.bits[q])
        return None

    def show_final_key(self):
        return self.final_key


class Bob:

    def __init__(self, num_bits):
        self.measurements = []
        self.final_key = []
        self.num_bits = num_bits
        self.bases = randint(2, size=num_bits)

    def receive_message(self, message):
        backend = Aer.get_backend('qasm_simulator')
        for q in range(self.num_bits):
            if self.bases[q] == 0:  # measuring in Z-basis
                message[q].measure(0, 0)
            if self.bases[q] == 1:  # measuring in X-basis
                message[q].h(0)
                message[q].measure(0, 0)
            qasm_sim = Aer.get_backend('qasm_simulator')
            qobj = assemble(message[q], shots=1, memory=True)
            result = qasm_sim.run(qobj).result()
            measured_bit = int(result.get_memory()[0])
            self.measurements.append(measured_bit)
        return None

    def declare_bases(self):
        return self.bases

    def gen_final_key(self, a_bases):
        self.final_key = []
        for q in range(self.num_bits):
            if self.bases[q] == a_bases[q]:
                self.final_key.append(self.measurements[q])
        return None

    def show_final_key(self):
        return self.final_key


class Eve:

    def __init__(self):
        self.num_bits = 0
        self.new_message = []
        self.key = []

    def read_message(self, message):
        self.num_bits = len(message)
        return None

    def create_new_message(self):
        return self.new_message

    def show_key(self):
        return self.key


def generate_key(intercept=False):
    num_bits = 10
    alice = Alice(num_bits)
    bob = Bob(num_bits)

    if intercept:
        print("\n Communication with Interception from Eve")
    else:
        print("\n Communication without interception")

    message = alice.send_message()

    if intercept:
        eve = Eve()
        # eve.read_message(message)
        # message = eve.create_new_message()

    bob.receive_message(message)

    a_bases = alice.declare_bases()
    b_bases = bob.declare_bases()

    alice.gen_final_key(b_bases)
    bob.gen_final_key(a_bases)

    print(alice.show_final_key(), " Key at Alice's side")
    print(bob.show_final_key(), " Key at Bob's side")
    if intercept:
        print(eve.show_key(), " Key at Eve's side")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        generate_key(intercept=True)
    else:
        generate_key()
