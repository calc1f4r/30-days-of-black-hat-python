from PyPDF2 import PdfFileReader,PdfFileWriter
from os import path
from sys import exit
from termcolor import colored

def bruteforcepdf(pdfFile,wordlistfile):
    """Function to bruteforce pdf file"""
    passwords=[]
    with open(wordlistfile,'r') as f:
        for password in f.readlines():
            passwords.append(password.strip())
            
    reader=PdfFileReader(pdfFile)
    for password in passwords:
        if str(reader.decrypt(password))=='PasswordType.OWNER_PASSWORD':
            print(colored(f"[+] Password Found : {password}",'green',attrs=['bold']))
            return password
            break


def decrypt_pdf(encypted_file,decrypted_file,password):
    with open(encypted_file,'rb') as encryptedFile, open(decrypted_file,'wb') as decrypteFile:
        reader=PdfFileReader(encryptedFile)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer=PdfFileWriter()
        for i in range(reader.getNumPages()):
            writer.addPage(reader.getPage(i))
        writer.write(decrypted_file)
    print(colored(f"File Has been Succcessfully decrypted and saved at : {decrypted_file}",'cyan'))


if __name__=="__main__":
    pdfFile=input("[+] Enter the location of Password Protected File Pdf : ")
    if not path.exists(pdfFile):
        print(colored("[-] Please specify the location of Pdf file accurately ",'red'))
        exit(-1)

    
    wordlistfile=input("[+] Enter the location of password wordlist file: ")
    if not path.exists(wordlistfile):
        print(colored("[-] Please specify the location of wordlist file accurately ",'red'))
        exit(-1)


    password=bruteforcepdf(pdfFile,wordlistfile)
    if password:
        decrypt_pdf(pdfFile,f"decrypted-{path.basename(pdfFile)}",password)
    else:
        print(colored("[-] Password was not Found :",'red'))