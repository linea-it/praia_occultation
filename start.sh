
# Para fazer alteraçoes em algum script e testar de forma mais facil, copia o script para a pasta teste e executa com essa instrucao
# docker run -it --rm --name praia_occ --volume $PWD/data:/data --volume $PWD/:/app  praia-occultation:latest python run.py


# Exemplo de como executar o comando generate_dates
docker run -it --rm \
    --name praia_occ \
    --volume $PWD/data:/data \
    --volume $PWD/:/app  \
    praia-occultation:latest  \
    ./generate_dates.py '2018-JAN-01' '2018-DEC-31 23:59:01' 60