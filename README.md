# praia_occultation
## Requisitos
Docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04


## User
### Download da imagem versão estavel 
```
docker pull linea/praiaoccultation:latest
```

### Executar o bash dentro do Container 
```
docker run -it --rm --name praia_occ --volume $PWD/data:/data --volume $PWD/:/app linea/praiaoccultation:latest /bin/bash
```
### Executar a geração de mapas, os inputs devem estar no diretório data
```
docker run -it --rm --name praia_occ --volume $PWD/data:/data --volume $PWD/:/app linea/praiaoccultation:latest python generate_maps.py 1996RR20 200 g4_occ_data_JOHNSTON_2018_table
```


## Develop
### Comando para fazer o Build do Container
```
docker build -t linea/praiaoccultation:latest .
```
