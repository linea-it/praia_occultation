# praia_occultation
## Requisitos
Docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04

## User
### Download da imagem versão estavel 
```
docker pull linea/praiaoccultation:latest
```

TODO:  lista com todos os comandos possiveis.

### Executar a geração de mapas, os inputs devem estar no diretório data
```
docker run -it --rm --volume $PWD/data:/data linea/praiaoccultation:latest python generate_maps.py 1996RR20 200 g4_occ_data_JOHNSTON_2018_table
```
para acompanhar a execução basta olhar o arquivo maps.log dentro do diretório data. 
```
tail -f data/maps.log
```
obs: o tail é executado em outro terminal fora do container.


### Executar o bash dentro do Container 
```
docker run -it --rm --volume $PWD/data:/data linea/praiaoccultation:latest bash
```

# Development

Repositório: https://github.com/linea-it/praia_occultation

## Clone do repositório 
```
git clone https://github.com/linea-it/praia_occultation.git 
```
entrar no diretório 
```
cd praia_occultation
```

## Execução e Alteração dos códigos. 
Para alterar os scripts dentro do container é necessário montar o diretório que foi clonado como volume. 
```
docker run -it --rm --volume $PWD/data:/data --volume $PWD:/app linea/praiaoccultation:latest bash
```


### Comando para fazer o Build do Container
```
docker build -t linea/praiaoccultation:latest .
```

### Update da imagem no docker cloud
Logar no docker cloud.
```
docker login
```
Fazer o push da imagem
```
docker push linea/praiaoccultation:latest
```


