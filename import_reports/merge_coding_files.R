
library(dplyr)
library(countrycode)



# Read coding files
fariss <- tbl_df(read.csv('../../data/coding_files/latent_repression.csv',
                          header = TRUE, stringsAsFactors = FALSE))
ciri_empowerment <- tbl_df(read.csv('../../data/coding_files/ciri_empowerment.csv',
                                    header = TRUE, stringsAsFactors = FALSE))

combined <- left_join(fariss, ciri_empowerment, by = c("COW", "YEAR"))

# put in iso3c codes
combined$country_iso3c <- countrycode(as.integer(combined$COW), origin = "cown", destination = "iso3c")
combined$country_name <- countrycode(as.integer(combined$COW), origin = "cown", destination = "country.name")

# Delete unnecesary columns
combined$CIRI.x <- NULL
combined$CTRY <- NULL

colnames(combined)[c(1, 2, 18)] <- c("Year", "country_cow", "CIRI")
 
# Write output to file
write.csv(combined, "../../data/coding_files/hr_codings.csv",
          row.names = FALSE)

