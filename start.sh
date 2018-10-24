
# Para fazer alteraçoes em algum script e testar de forma mais facil montar o volume app 
# docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app \
#     praia-occultation:latest \
#     /bin/bash


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

# Exemplo de como executar o PRAIA OCC
# docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app  \
#     praia-occultation:latest  \
#     python search_candidate_stars.py /data/PRAIA_occ_star_search_12.dat


# Exemplo de comando para executar o programa de Mapas
#   docker run -it --rm \
#     --name praia_occ \
#     --volume $PWD/data:/data \
#     --volume $PWD/:/app \
#     praia-occultation:latest \
#     python generate_maps.py 1999RB216 147 g4_occ_data_JOHNSTON_table