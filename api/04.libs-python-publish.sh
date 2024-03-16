devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use root/dev

export TWINE_PASSWORD=
# twine upload -u root --repository-url http://localhost:3141/root/dev python/market_rpc/dist/*
for dir in ./schema/*/     # list directories in the form "/tmp/dirname/"
do
    dir=${dir%*/}      # remove the trailing "/"
    aaa=${dir##*/}
    echo "${aaa}"    # print everything after the final "/"
    twine upload -u root --repository-url http://localhost:3141/root/dev python/$aaa/dist/*
done