from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer
from numpy.random import randint


class ThirdParty:

    def __init__(self, num_bits):
        self.a_electrons = []
        self.b_electrons = []
        self.num_bits = num_bits

    def create_entangled_electrons(self):
        for i in range(self.num_bits):
            qr = QuantumRegister(2, name="qr")
            cr = ClassicalRegister(4, name="cr")
            qc = QuantumCircuit(qr, cr)
            qc.x(qr[0])
            qc.x(qr[1])
            qc.h(qr[0])
            qc.cx(qr[0], qr[1])
            # qc.draw(output="mpl")
            self.a_electrons.append(qr[0])
            self.b_electrons.append(qr[1])
        return self.a_electrons, self.b_electrons


class Alice:

    def __init__(self, num_bits, electrons):
        self.final_key = []
        self.num_bits = num_bits
        self.electrons = electrons
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

    def __init__(self, num_bits, electrons):
        self.measurements = []
        self.final_key = []
        self.electrons = electrons
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


def generate_key():
    num_bits = 10
    third_party = ThirdParty(num_bits)

    a_electrons, b_electrons = third_party.create_entangled_electrons()
    alice = Alice(num_bits, a_electrons)
    bob = Bob(num_bits, b_electrons)

    message = alice.send_message()
    bob.receive_message(message)

    a_bases = alice.declare_bases()
    b_bases = bob.declare_bases()

    alice.gen_final_key(b_bases)
    bob.gen_final_key(a_bases)

    print(alice.show_final_key())
    print(bob.show_final_key())


if __name__ == '__main__':
    generate_key()
