
# Para fazer alteraçoes em algum script e testar de forma mais facil, copia o script para a pasta teste e executa com essa instrucao
# docker run -it --rm --name praia_occ --volume $PWD/data:/data --volume $PWD/:/app  praia-occultation:latest python run.py


# # Exemplo de como executar o comando generate_dates
# docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app  \
#     praia-occultation:latest  \
#     ./generate_dates.py '2018-JAN-01' '2018-DEC-31 23:59:01' 600

# # Exemplo de como executar o comando generate_ephemeris
# docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app  \
#     praia-occultation:latest  \
#     python generate_ephemeris.py dates.txt 1999RB216.bsp de435.bsp 1999RB216.eph

# # Executar o Bash dentro do container
# docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app  \
#     praia-occultation:latest  \
#   python generate_ephemeris.py dates.txt 1999RB216.bsp de435.bsp 1999RB216.ephsh


