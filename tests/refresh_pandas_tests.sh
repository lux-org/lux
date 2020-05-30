echo ""
echo "This should be run from within the 'lux/tests' folder"
echo ""
rm -rf ./pandas_tests
rm -rf ./pandas
git clone https://github.com/pandas-dev/pandas
cp -R ./pandas/pandas/tests ./pandas_tests
sudo rm -r pandas
