# praia_occultation

Essa é uma imagem docker criada para executar o processo de Refinamento de Orbita e predição de ocultações para objetos no sistema solar. O refinamento de Orbita é feito utilizando o NIMAv7 e a predição utiliza o PRAIA_occ_star_search.

O Objetivo é facilitar o uso dessas duas aplicações, no contexto do portal TNO do LIneA.

Essa imagem apesar de poder ser utilizada de forma independente do portal, não recomendo esse uso por que tudo foi otimizado para o ambiente do LIneA.

## Requisitos

* Docker
* Acesso a um banco de dados contendo uma tabela do GAIA DR2 usado na etapa de predição.
* Um diretório onde o usuario que vai executar a imagem tenha permissão de escrita.

### Download da imagem versão estavel

```
docker pull linea/praiaoccultation:latest
```

TODO:  lista com todos os comandos possiveis.

## Forma de utilizar a imagem

A imagem processa um unico objeto por vez.

É necessário ter um diretório com os arquivos de inputs para o objeto antes de iniciar a execução da imagem são eles:

### Para o refinamento de Orbita NIMAv7

4 inputs are required, they must have the target name (without spaces and without "_") and its extension. For example: the target 1999 RB216 has the following inputs:

```bash
.
└── 1999_RB216
    ├── 1999RB216.eq0
    ├── 1999RB216.rwo
    ├── 1999RB216.txt
    └── 1999RB216.bsp
```

#### Astrometric positions

The user must provide an ascii file per object with astrometric positions which were determined using some astrometric package. See the example for the case 1999RB216.txt for knowing the format of this file. The columns are composed by:

* Right Ascension (col. 1-3) in HH MM SS format
* Declinations (col. 4-6) in DD MM SS format
* Observed magnitude (col. 7)
* Julian Date (col. 8)
* Code of the observer location (col. 9). See IAU code
* Reference stellar catalogue (col. 10). See MPC code

#### Observational history

Positions already determined from the observational history of objects. 1999RB216.rwo and 1999RC216.rwm are examples of observation files which were downloaded from AstDyS and MPC respectively.

Note that this files have to keep the original formats and the user only has to define the extension of file names:

* .rwo for AstDyS source
* .rwm for MPC source

AstDyS must be considered as the first option for getting the observation history (and orbital elements too).

#### Orbital elements

Orbital elements are the parameters required to uniquely identify a specific orbit. [1999RB216.eq0](https://github.com/linea-it/nima/blob/master/example/1999RB216.eq0) and [1999RC216.eqm](https://github.com/linea-it/nima/blob/master/example/1999RC216.eqm) are examples of files with orbital elements which were downloaded from [AstDyS](http://hamilton.dm.unipi.it/astdys2/) and [MPC](https://www.minorplanetcenter.net/) respectively.

In the case of MPC the user has to create a ascii file with the next parameters (one parameter per line):

01. Provisional name of object
02. Object number ("no" if unnumbered object)
03. Designation name of object ("no" if unnamed object)
04. Epoch
05. Epoch JD
06. Argument of perihelion (degrees)
07. Mean anomaly (degrees)
08. Ascending node (degrees)
09. Inclination (degrees)
10. Eccentricity
11. Semimajor axis (au)
12. Absolute magnitude
13. Phase slope

In the [site](https://minorplanetcenter.net/db_search/show_object?object_id=1999+RC216) are all the parameters above mentioned for the case of object *1999 RC216*.

Note that this files have to keep the original formats and the user only has to define the extension of file names:

* .eq0 for AstDyS source
* .eqm for MPC source

#### Object ephemeris

The state vector of a given body at any time is derived from bsp (Binary Spacecraft and Planet Kernel) file which contents the object ephemeris. Bsp files can be downloaded using the script smb_spk through expect language. 

O arquivo deve se chamar asteroid_name.bsp exemplo 1999RB216.bsp

### Para a Predição de Ocultação PRAIA

Para a etapa de predição, é necessário o arquivo de Object ephemeris, que pode ser o mesmo usado para o refinamento ou o bsp gerado pelo nima. É necessário também que a imagem tenha acesso a um banco de dados que contenha a tabela do GAIA DR2. esse ponto é que torna a imagem inviavel para ser usada fora do ambiente do linea, por outro lado é o que simplifica o seu uso no pipeline do portal. no futuro pode ser implementado uma forma de ler esses dados de arquivos.

### Running

A Execução desta imagem é relativamente simples, quando usada pelo pipeline do portal TNO, a imagem conta com um script principal que recebe alguns parametros e executa as 2 aplicações em sequencia.

O script run.py já verifica os inputs e registra os logs e informaçoes da execução. Tudo que é gerado pelos programas ficam armazendos no diretório do objeto o mesmo que contem os inputs. Internamente na imagem esse diretório é um link para /tmp/data isso permite que os programas possam acessar todos os arquivos sem se preocupar com o path externo.

A quantidade de parametros foi reduzida por questão de praticidade mas no futuro mais parametros podem ser adicionados, no momento é usado uma configuração padrão para todos os objetos. esses parametros estão nos arquivos src/nima_input_template.txt e src/praia_occ_input_template.txt

O resultado principal da execução é o arquivo **Occultation table** que contem os eventos de ocultação que foram previstos para o objeto dentro do periodo informado nos parametros.

Uma observação importante sobre a execução é que antes da execução dos programas se houver arquivos de uma execução anterior para o mesmo objeto estes serão removidos.

#### Como utilizar o script run.py

O script run.py recebe os seguintes argumentos e a partir deles ele cria os arquivos de parametros para o NIMAv7 e o PRAIA_occ, e controla a execução dos mesmos de forma sequencial.

Os Parametros são:

* name (Obrigatório) - Object name without spaces. example 1999RB216
* start_date (Obrigatório) - Data inicial do periodo que sera feita a predição, também é usado na geração do bsp do Nima. o formato deve ser YYYY-MM-DD exemplo: 2021-01-15
* final_date (Obrigatório) - Data final do periodo que sera feita a predição, também é usado na geração do bsp do Nima. o formato deve ser YYYY-MM-DD exemplo: 2022-12-31

esses 3 parametros são o minimo para a execução são obrigatórios e posicionais.

os demais parametros são opcionais e já possuem valores predefinidos:

* --number - Asteroid number. if not informed, the name will be used. example 137295.
* --step - steps in seconds. Example 60 utilizado na predição, inflencia nas querys feitas para recuperar as estrelas no caminho do objeto.
* --leap_sec - Name of the Leap Seconds file exemplo naif0012.tls, este arquivo já está na imagem, caso seja necessário utilizar outro arquivo ele deve estar no diretório dos inputs.
* --bsp_planetary - Name of the BSP Planetary file exemplo de435.bsp, este arquivo já esta na imagem, caso seja necessário utilizar outro arquivo ele deve estar no diretório dos inputs
* --bsp_object - Name of the Asteroid BSP file, it must be in the directory. example Eris.bsp. default asteroid_name.bsp
* --path - Path where the inputs are and where the outputs will be. must be the path as it is mounted on the volume, should be used when it is not possible to mount the volume as /tmp/data. example the inputs are in /archive/asteroids/Eris and this path is mounted inside the container the parameter --path must have this value --path /archive/asteroids/Eris, the program will create a link from this path to /tmp/data.

#### Executando a Imagem docker

```bash
docker run -it --rm --user 10139:10000 --volume /home/glauber/linea/1999RB216:/home/glauber/linea/1999RB216 --network host -e DB_URI=postgresql+psycopg2://postgres:postgres@172.18.0.2:5432/tno_v2 linea/praiaoccultation:v2.8.2 python run.py 1999RB216 2021-10-01 2023-01-01 --number 137295 --step 600 --path /home/glauber/linea/1999RB216
```

Levando em consideração que está imagem foi criada para ser usada no ambiente do LIneA especificamente pelo HTCondor, este comando está simulando o comportamento da imagem quando é executada no condor.

primeiro parte do comando `docker run -it --rm` é o comando padrão para o docker criar um container a partir da imagem e executar um processo e remover o container após a execução.

Quando a imagem é executada pelo HTCondor ele vai executar o container com o usuario e grupo que submeteu o job, isto está simulado no parametro `--user 10139:10000` onde o user é 10139 e o grupo é 10000.

Para os inputs é necessário montar um volume com o diretório do objeto. neste exemplo é essa parte `--volume /home/glauber/linea/1999RB216:/home/glauber/linea/1999RB216` repare que é necessário montar o path no container da mesma forma como ele está no host, isso é por causa da forma como os programas vão interagir com esses arquivos e pelo fato do HTCondor ter um unico volume montado, isso faz sentido com o parametro --path do comando run.py.

Como essa imagem internamente vai fazer conexão com banco de dados que é um serviço externo a maquina do HTCondor é necessário que o container tenha acesso a mesma rede do Host `--network host` . aparentemente o HTCondor quando levanta os container já o faz com essa configuração.

Para a comunição com o bando de dados, é necessário uma variavel de ambiente BD_URI que é uma string de conexão com o banco de dados postgres que contem a tabela do GAIA DR2 neste exemplo é uma uri para um bando de desenvolvimento `DB_URI=postgresql+psycopg2://postgres:postgres@172.18.0.2:5432/tno_v2` .

`linea/praiaoccultation:v2.8.2` está parte do comando é o nome da imagem e sua versão que será usada. para saber a versão acessar o https://hub.docker.com/repository/docker/linea/praiaoccultation Essa versão está fixada pelo desenvolvedor no pipeline do portal TNO não é recomendado alterar a versão se não tiver certeza.

Essa parte é o comando que será executado assim que o container ficar pronto.
`python run.py 1999RB216 2021-10-01 2023-01-01 --number 137295 --step 600 --path /home/glauber/linea/1999RB216` neste exemplo o nome do asteroid é 1999RB216 o periodo que será feito as predições é 2021-10-01 - 2023-01-01 o Number é o numero do objeto, step é o intervalo em segundo que será utilizado para calcular as posições das querys no caminho do objeto, e --path é o diretório onde estão os inputs. quando o container é executado no HTCondor o volume montado é fixo exemplo /archive/tno/asteroids mas a execução é para um objeto especifico nesse caso o parametro --path deve conter o path completo para o diretório do objeto tipo /archive/tno/asteroids/1999RB216.

Exemplo de um arquivo de submissão no HTCondor para está imagem:

```bash
Universe       = docker
docker_image   = linea/praiaoccultation:v2.8.2
Executable     = /usr/local/bin/python
Arguments      = /app/run.py 1999RB216 2021-10-01 2023-01-01 --number 137295 --step 600 --path /archive/tno/asteroids/1999RB216
environment    = DB_URI=postgresql+psycopg2://user:password@desdb4.linea.gov.br:5432/prod_gavo
docker_network_type = host
initialdir     = /archive/tno/asteroids/1999RB216
Output         = /archive/tno/asteroids/1999RB216/condor.out
Error          = /archive/tno/asteroids/1999RB216/condor.err
Log            = /archive/tno/asteroids/1999RB216/condor.log
Queue 1
```

para acompanhar a execução basta olhar os arquivos de logs nima.log e praia_occ.log dentro do diretório do objeto.

# Development

Repositório: <https://github.com/linea-it/praia_occultation>

## Clone do repositório

```
git clone https://github.com/linea-it/praia_occultation.git 
```

entrar no diretório

```
cd praia_occultation
```

## Execução e Alteração dos códigos

Para alterar os scripts dentro do container é necessário montar o arquivo que se deseja alterar como volume exemplo alterando o arquivo run.py.

```bash
docker run -it --rm --user 10139:10000 --volume /home/glauber/linea/1999RB216:/home/glauber/linea/1999RB216 --volume /home/glauber/linea/praia_occultation/src/run.py:/app/run.py --network host -e DB_URI=postgresql+psycopg2://postgres:postgres@172.18.0.2:5432/tno_v2 linea/praiaoccultation:v2.8.2 python run.py 1999RB216 2021-10-01 2023-01-01 --number 137295 --step 600 --path /home/glauber/linea/1999RB216
```

### Comando para fazer o Build do Container

```bash
docker build -t linea/praiaoccultation:v2.x.x .
```

### Update da imagem no docker cloud

Logar no docker cloud.

```bash
docker login
```

Fazer o push da imagem

```bash
docker push linea/praiaoccultation:v2.x.x
```
