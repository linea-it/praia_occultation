# praia_occultation

# Comando para fazer o Build do Container
# docker build -t linea/praiaoccultation:latest .


# Executar o bash dentro do Container 
```
docker run -it --rm --name praia_occ --volume $PWD/data:/data --volume $PWD/:/app linea/praiaoccultation:latest /bin/bash
```