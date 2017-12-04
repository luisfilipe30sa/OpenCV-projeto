# =============================================
# Conta Alevinos
# =============================================
#
#Código baseado no projeto pacu do professor 
#   Hemerson Pistori (pistori@ucdb.br)
#
#===============================================================================

import tkMessageBox
import numpy as np
import cv2
import RPi.GPIO as gpio
import time


gpio.setwarnings(False)


# Valores minimos e maximos definidos manualmente para
# serem utilizados na limiarizacao no espaco BGR
minCor = (50,49,52)
maxCor = (67,61,70)

# Tamanho minimo e maximos (com valores extremos pois
# ainda nao estao sendo usados para valer)
minTamanho = 1
maxTamanho = 20000000

# Distancia em relacao ao centro anterior (se o centro anterior do alevino
# estiver a uma distancia menor que esta, considera-se que trata-se
# do mesmo peixe)
erroDistancia = 0

# Abre a camera
video = cv2.VideoCapture(0)

#forca a camera a ter resolucao 640x480
video.set(3,160)
video.set(4,120)

# Carrega o banner com as logos
banner = cv2.imread('banner.png')

# Le o primeiro quadro/frame do video
ret, quadro = video.read()

# Pega as dimensoes do quadro
altura, largura, canais = quadro.shape

# Define qual a linha sera utilizada como "linha de chegada". Quando
# os alevinos passam por esta linha e que sao contados
lin = altura - 40

# Contador de alevinos que vai sendo incrementado
totalAlevinos = 0

totalFinal = 10

# Desenha uma janela retangular ao redor da linha de chegada
janelaChegada = (0, lin - 1, largura - 1, lin + 1)

# Guarda os valores dos centros dos alevinos encontrados no
# quadro anterior. Como apenas uma linha e analisada, basta
# guardar a coordenada y do centro
ultimosCentros = []

# Apenas para parar depois de mostrar o primeiro quadro
primeiroQuadro = True

# Dentro deste laco serao lidos todos os quadros do video
while (ret == True):

    linha = quadro[lin:lin+1,0:largura]  # Pega a linha de chegada
    linhaMaisGrossa  = cv2.resize(linha, (largura, 100))  # Engrossa em 100 vezes a linha para permitir
                            # uma melhor visualizacao e tambem a aplicacoes de morfologia matematica e
                            # deteccao de contornos

    linhaSegmentada = cv2.inRange(linhaMaisGrossa, minCor, maxCor ) # Limiarizacao no espaco BGR
    nucleo = np.ones((3,3),np.uint8)    # Nucleo para a operacao morfologica
    linhaFiltrada = cv2.dilate(linhaSegmentada,nucleo,iterations = 2)
    linhaFiltrada = cv2.erode(linhaFiltrada,nucleo,iterations = 2)
    cv2.imshow('Linha Filtrada',linhaFiltrada)

    # Detecta os contornos (na linha ampliada)
    linhaContornos, contornos, hierarquia = cv2.findContours(linhaFiltrada,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    #print 'Encontrou %d contornos -------------' % len(contornos)

    novosCentros = []
    for contorno in contornos:
        momentos = cv2.moments(contorno)

        tamanho = momentos['m00']

        if momentos['m00'] > 0:   # Nunca deveria ser 0, mas esta ocorrendo com colunas de tamanho 1
            posicao = int(momentos['m10']/momentos['m00'])

       # print 'tamanho = %d' % tamanho
       # print 'posicao = %d' % posicao

        # A linha abaixo esta sem efeito pois os valores minimos e maximos sao extremos. Tem que melhor isso.
        if tamanho > minTamanho and tamanho < maxTamanho:

            jaContou = False

            # Verificando se no quadro anterior tinha algum centro proximo
            for posicaoAnterior in ultimosCentros:
                if abs(posicaoAnterior-posicao) < erroDistancia:
                    jaContou = True

            # Se ja nao foi contado no quadro anterior, conta e guarda o centro
            if not jaContou:
                totalAlevinos += 1
                novosCentros = novosCentros + [posicao]

    ultimosCentros = novosCentros

    # Mostra a linha de chegada e o texto com a contagem
    quadroResultado = cv2.rectangle(quadro,janelaChegada[0:2],janelaChegada[2:4],(20,200,20),1)
    quadroResultado = cv2.putText(quadroResultado,'Contagem = '+str(totalAlevinos),(largura/2-50,lin+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,100,250),2)

    # Mostra o video e as janelas com resultados intermediarios
    cv2.imshow('Contador', banner)
    cv2.imshow('Entrada', quadroResultado)
    #cv2.imshow('Linha',linhaMaisGrossa)
    #cv2.imshow('Linha Segmentada',linhaSegmentada)

    # Ajusta as posicoes das janelas para nao ficar uma em cima da outra
    cv2.moveWindow('Contador', 0,0)
    cv2.moveWindow('Entrada', 30, 150)
    #cv2.moveWindow('Linha',160,110)
    #cv2.moveWindow('Linha Segmentada',160, 210)
    cv2.moveWindow('Linha Filtrada',250, 150)

    # Mostra o video em camera lenta. Se teclar 'ESC' sai do programa
    k = cv2.waitKey(50) & 0xff
    if( k == 27):
        break
    elif (k == 32):
        k = cv2.waitKey() & 0xff
        cv2.destroyAllWindows()
        
    ret, quadro = video.read()
    # Configurando como BOARD, Pinos Fisicos
    gpio.setmode(gpio.BOARD)
    # Configurando a direcao do Pino
    gpio.setup(32, gpio.OUT)
    gpio.setup(36, gpio.OUT)
    gpio.setup(38, gpio.OUT)
    gpio.setup(40, gpio.IN)
    if(totalAlevinos<totalFinal):
        gpio.output(32, gpio.HIGH)
        gpio.output(36, gpio.HIGH)
        gpio.output(38, gpio.LOW)    
            
    # Configurando como BOARD, Pinos Fisicos
    gpio.setmode(gpio.BOARD)
    # Configurando a direcao do Pino
    gpio.setup(32, gpio.OUT)
    gpio.setup(36, gpio.OUT)
    gpio.setup(38, gpio.OUT)
    gpio.setup(40, gpio.IN)
    if(totalAlevinos>=totalFinal):
        gpio.output(32, gpio.LOW)
        gpio.output(36, gpio.LOW)
        gpio.output(38, gpio.HIGH)
    if gpio.input(40) == gpio.HIGH:
        totalAlevinos=0
        time.sleep(10)
        gpio.output(38, gpio.LOW)
        exit()
    
cv2.destroyAllWindows()
gpio.cleanup()

