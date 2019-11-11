#get mysql image
docker pull mysql

#create desired mysql image and run
docker-compose -f stack.yml up

#if you want to restart:
# docker rmi mysql
#then run this script again
