# s3-cost-calculator

```
usage: s3calc [-h] [--region REGION] [--config CONFIG] [--gb GB] [--number_of_objects NUMBER_OF_OBJECTS] [--outfile OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       Region to look at in the pricing_info.yml file.
  --config CONFIG       Path to config file.
  --gb GB               Total size of data in GiB
  --number_of_objects NUMBER_OF_OBJECTS
                        Number of objects to transition.
  --outfile OUTFILE     Name / path to write output csv file.
```

By default the application will use the pricing config file located in [pricing_info.yml](./src/s3calc/pricing_info.yml). 
You can pass in another config file with updated prices by passing in another config file using the `--config` flag.

Note that pricing for the Glacier and Deep Glacier retrieval costs assumes that the data will be stored temporarily for 14 days.