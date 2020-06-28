import os #thu vien cho xu li voi file
import numpy as np #thu vien xu li voi ma tran
import argparse #thu vien xu li tham so input
import matplotlib.pyplot as plt #thu vien hien thi anh

#chuyen dang text sang dang day bit
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

#chuyen dang day bit ve dang text
def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

#xor hai day bit voi nhau
def xor(x, y):
    return '{1:0{0}b}'.format(len(x), int(x, 2) ^ int(y, 2))

#tinh toan gia tri cua x1, x2 dua vao mang hopfield
def updateX(x1, x2):
    x1_t = x1[1] / 4.0 + np.sin(x2[0])
    x2_t = x2[2] * 3.0 / 4.0 - 2.0 * np.tanh(x1[0])
    x1[0] = x1[1]
    x1[1] = x1_t
    x2[0] = x2[1]
    x2[1] = x2[2]
    x2[2] = x2_t

#hien thi map cua mang hopfield sau N lan lap
x1 = np.array([0.01, 0.01])
x2 = np.array([0.01, 0.01, 0.01])
X = []
Y = []
for i in range(1000): #chinh sua so lan lap tai day
    updateX(x1, x2)
    # plt.plot(x1[1], x2[2])
    X.append(x1[1])
    Y.append(x2[2])
plt.plot(X, Y)
plt.show()
abc

#lay bit thu 4 tu gia tri x duoc tao ra moi lan lap
def getBinarySequence(b, x, d, e, step):
    for r in range(1, 16):
        theta_t = (e-d)*(r/16) + d
        if x >= theta_t:
            b[step] += (-1)**(r-1)

#lay 38 bit thu 4 sau 38 lan lap
def get38Bits(choose):
    b = np.zeros(38).astype(int)
    if choose == '0':
        d = -1.5
        e = 1.5
        for i in range(38):
            updateX(x1, x2)
            getBinarySequence(b, x1[1], d, e, i)
    elif choose == '1':
        d = -4
        e = 5
        for i in range(38):
            updateX(x1, x2)
            getBinarySequence(b, x2[2], d, e, i)
    return b

#chia 38 bit thanh A0, D1, A2
def getA(s):
    A0 = ''
    A1 = ''
    A2 = ''
    for i in range(32):
        A0 += str(s[i])
    for i in range(32, 37):
        A1 += str(s[i])
    A2 += str(s[37])
    D1 = int((A1[0])) * 16 + int((A1[1])) * 8 + int((A1[2])) * 4 + int((A1[3])) * 2 + int((A1[4]))
    return A0, D1, A2

#dich bit xoay vong theo ben trai
def leftRotate(s, n):
    return s[n:] + s[:n]

#dich bit xoay vong theo ben phai
def rightRotate(s, n):
    return s[32-n:] + s[:32-n]

#ham main
if __name__ == '__main__':
    #khoi tao cac tham so khi chay file
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, help="enc for encryption or dec for decryption") #kieu (ma hoa, giai ma)
    parser.add_argument("--file", type=str, help="location of file to encrypt or decrypt data")#ten file
    opt = parser.parse_args()
    type_aim = opt.type
    filename = opt.file

    #khoi tao gia tri ban dau cho mang hopfield
    x1 = np.array([0.01, 0.01])
    x2 = np.array([0.01, 0.01, 0.01])

    #lap dao dau 10000 lan
    for i in range(10000):
        updateX(x1, x2)

    #doc file
    with open(filename, 'r') as fopen:
        message = fopen.read()

    #neu la ma hoa thi kiem tra xem do dai file co chia het cho 32 khong, neu khong thi dien day vao cuoi theo quy tac:
    #neu bit cuoi la 0 thi dien day 1, neu bit cuoi la 1 thi dien day 0
    #sau do so bit dien day duoc bieu dien bang 2 byte va ghi vao dau file ma hoa
    if type_aim == "enc":
        fwrite = open(f'{filename}.enc', 'a+')
        mess_bits = text_to_bits(message)
        if len(mess_bits) % 32 != 0:
            residual = 32 - len(mess_bits) % 32
            if mess_bits[-1] == '1':
                mess_bits += '0' * residual
            else:
                mess_bits += '1' * residual
            residual = hex(residual)[2:]
            if len(residual) < 2:
                residual = '0' * (2 - residual) + residual
        else:
            residual = '00'
        fwrite.write(residual)
    else: #neu la giai ma thi doc 2 byte dau de biet bao nhieu bit duoc dien day
        residual = message[:2]
        residual = int(residual, 16)
        message = message[2:]
        fwrite = open(filename[:-4], 'a+')
        num_of_bits = len(message) * 4
        mess_bits = bin(int(message, 16))[2:].zfill(num_of_bits)

    #so block can max hoa hoac giai ma (moi block 32 bit)
    numBlocks = int(len(mess_bits) / 32)
    
    #ma hoa block dau cua file can ma hoa
    if type_aim == "enc":
        P0 = mess_bits[:32] #plaintext
        sequenceBits = get38Bits('0').astype(int) #day 38 bit
        A0, D1, A2 = getA(sequenceBits) #chia thanh A0, D1, A2
        A0_D = rightRotate(A0, D1) #xoay vong phai D1 bit cua A0
        P0_D = leftRotate(P0, D1) #xoay vong trai D1 bit cua P0
        C0 = xor(A0_D, P0_D) #xor P0_D voi A0_D duoc ciphertext
        cipher = hex(int(C0, 2))[2:] #ciphertext dang hexa
        if len(cipher) < 8:
            cipher = '0' * (8 - len(cipher)) + cipher #them byte 0 vao dau de cipher dung 8 byte
        fwrite.write(cipher) #viet ra file
    else: #giai ma block dau cua file can giai ma
        C0 = mess_bits[:32]
        sequenceBits = get38Bits('0').astype(int)
        A0, D1, A2 = getA(sequenceBits)
        A0_D = rightRotate(A0, D1)
        P0_D = xor(A0_D, C0)
        P0 = rightRotate(P0_D, D1)
        fwrite.write(text_from_bits(P0))

    #ma hoa hoac giai ma cac block sau block dau
    for i in range(1, numBlocks):
        for j in range(D1):
            updateX(x1, x2)
        sequenceBits = get38Bits(A2)
        A0, D1, A2 = getA(sequenceBits)
        A0_D = rightRotate(A0, D1)
        if type_aim == "enc":
            P = mess_bits[32*i : 32*(i+1)]
            P_D = leftRotate(P, D1)
            C = xor(A0_D, P_D)
            cipher = hex(int(C, 2))[2:]
            if len(cipher) < 8:
                cipher = '0' * (8 - len(cipher)) + cipher
            fwrite.write(cipher)
        else:
            C = mess_bits[32*i : 32*(i+1)]
            P_D = xor(A0_D, C)
            P = rightRotate(P_D, D1)
            if i == numBlocks - 1 and residual != 0: #neu la block cuoi va co dien day bit luc ma hoa thi bo nhung bit dien day di
                fwrite.write(text_from_bits(P[:32-residual]))
            else:
                fwrite.write(text_from_bits(P))
    if type_aim == "enc":
        print("Your file has been encrypted succesfully!")
    else:
        print("Your file has been decrypted succesfully!")
    fwrite.close()
    os.remove(filename) #xoa file ban dau di