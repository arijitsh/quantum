from numpy.random import randint, rand
from qiskit import QuantumCircuit, Aer, assemble
import numpy as np
verb = False


class Alice:

    def __init__(self, num_bits):
        self.num_bits = num_bits
        self.bits = randint(2, size=num_bits)
        self.bases = randint(2, size=num_bits)

        self.b_message = []
        self.sift_bits = []
        self.test_bits = []
        self.final_key = []

    def create_send_message(self):
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

    def receive_message(self, message):
        self.b_message = message

    def measure_ctrl_bits(self, sift_bits):
        self.sift_bits = sift_bits
        return True

    def measure_test_bits(self):
        for sift_bit in self.sift_bits:
            if (rand() < 0.2) and (sift_bit == 1):
                self.test_bits.append(1)
            else:
                self.test_bits.append(0)
        return True, self.test_bits

    def declare_bases(self):
        return self.bases

    def gen_final_key(self):
        final_key = []
        for i in range(self.num_bits):
            if self.sift_bits[i] == 1 and self.test_bits[i] == 0 and self.bases[i] == 0:
                final_key.append(self.bits[i])
            elif verb:
                final_key.append(2)
        self.final_key = final_key
        return None

    def show_final_key(self):
        return self.final_key


class Bob:

    def __init__(self, num_bits):
        self.num_bits = num_bits
        self.bases = randint(2, size=num_bits)
        self.sift_bits = randint(2, size=num_bits)

        self.new_message = []
        self.raw_key = []
        self.final_key = []

    def receive_message_sift_or_reflect(self, message):
        backend = Aer.get_backend('qasm_simulator')
        for q in range(self.num_bits):
            if self.sift_bits[q] == 1:  # sift bits
                message[q].measure(0, 0)
                qasm_sim = Aer.get_backend('qasm_simulator')
                qobj = assemble(message[q], shots=100, memory=True)
                result = qasm_sim.run(qobj).result()
                result = int(result.get_memory()[0])
                self.raw_key.append(result)
                qc = QuantumCircuit(1, 1)
                if result == 1:
                    qc.x(0)
                self.new_message.append(qc)
            else:  # ctrl bits -- reflected
                self.new_message.append(message[q])
                self.raw_key.append(2)
        return self.new_message

    def declare_sift_bits(self):
        return self.sift_bits

    def gen_final_key(self, a_bases, test_bits):
        final_key = []
        for i in range(self.num_bits):
            if self.raw_key[i] < 2 and test_bits[i] == 0 and a_bases[i] == 0:
                final_key.append(self.raw_key[i])
            elif verb:
                final_key.append(2)
        self.final_key = final_key
        return None

    def show_final_key(self):
        return self.final_key


class Eve:

    def __init__(self):
        self.num_bits = 0
        self.new_message = []
        self.key = []

    def read_alice_message(self, message):
        self.num_bits = len(message)
        return None

    def read_bob_message(self, message):
        self.num_bits = len(message)
        return None

    def create_new_message(self):
        return self.new_message

    def show_key(self):
        return self.key


def generate_key(intercept=False):
    delta = 0.2
    target_num_bits = 10
    num_bits = int(8 * target_num_bits * (1 + delta))

    alice = Alice(num_bits)
    bob = Bob(num_bits)

    if intercept:
        eve = Eve()
        print("\n Communication with Interception from Eve")
    else:
        print("\n Communication without interception")

    message = alice.create_send_message()

    if intercept:
        eve.read_alice_message(message)
        message = eve.create_new_message()

    message = bob.receive_message_sift_or_reflect(message)

    if intercept:
        eve.read_bob_message(message)
        message = eve.create_new_message()

    alice.receive_message(message)
    a_bases = alice.declare_bases()
    sift_bits = bob.declare_sift_bits()

    is_correct = alice.measure_ctrl_bits(sift_bits)
    assert is_correct

    is_correct, test_bits = alice.measure_test_bits()
    assert is_correct

    alice.gen_final_key()
    bob.gen_final_key(a_bases, test_bits)

    if verb:
        print(np.array(test_bits), "test_bits")
        print(a_bases, "a_bases")
        print(sift_bits, "sift_bits")
        print(np.array(alice.bits), "a_raw_key")
        print(np.array(bob.raw_key), "b_raw_key")

    print(alice.show_final_key(), " Key at Alice's side")
    print(bob.show_final_key(), " Key at Bob's side")
    if intercept:
        print(eve.show_key(), " Key at Eve's side")


if __name__ == '__main__':
    generate_key()
    # generate_key(intercept=True)
