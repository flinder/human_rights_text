library(ggplot2)
library(countrycode)
library(dplyr)
library(tidyr)
library(randomForest)
library(doParallel)
library(edarf)
library(reshape2)
library(xtable)

##===============================================================================
## Plot settings
##
##===============================================================================

# width and height
w = 10 # inches
h = .6 * w
cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2",
               "#D55E00", "#CC79A7")
FILL <- scale_fill_manual(values = cbPalette)
COLOR <- scale_color_manual(values = cbPalette)
THEME <- theme(panel.background = element_rect(fill = "white", colour = "black"), 
               panel.grid.major = element_line(colour = "gray70"))

#===============================================================================
# Descriptives from wordcounts
#===============================================================================

## Load wordcounts file (Extracted from mongoDB with extract_data.sh
wc <- read.table("../../data/analyses_plos/all_reports.csv", sep = ",", header = TRUE)
wc <- tbl_df(wc)
colnames(wc) <- c("filename", "word_count")

## extract out country names and years
wc$year <- as.integer(gsub("[^0-9]", "", wc$filename))
wc$year <- as.integer(sapply(as.character(wc$year), substring, 1, 4))
wc$organization <- substr(wc$filename, 1, 2)
extract <- function(x) paste0(x[3:length(x)], collapse = " ")
wc$country <- sapply(strsplit(as.character(wc$filename), "_"), extract)
wc$country <- tolower(wc$country)
wc$country <- gsub("-", " ", wc$country)
wc$year[wc$year == 19980] = 1998
wc$organization <- plyr::revalue(wc$organization, c(HR = "Human Rights Watch", SD = "State Department", 
                                                    CR = "Lawyers Committee", AI = "Amnesty International"))

name_fix_table <- read.csv("../filename_recode.csv")
matches <- match(wc$country, name_fix_table$actual)
replacements <- ifelse(is.na(matches), wc$country, name_fix_table$replacement[matches])
wc$country <- replacements

wc$country_cln <- countrycode(wc$country, "country.name", "country.name")
write(as.character(unique(wc$country[is.na(wc$country_cln)])), file = "unrec_countries.txt")

## get cow codes
wc$country_cow <- countrycode(wc$country_cln, "country.name", "cown")

## Rename and clean up a bit
wc <- select(wc, -country) %>%
      rename(Organization = organization, Country = country_cln, Year = year) %>%
      group_by(Organization, Year)

## Coverage plot
counts <- wc %>%
          filter(!is.na(Country)) %>%
          group_by(Organization, Year) %>%
          summarise(count = length(unique(Country)))

pdat <- counts %>% group_by(Year) %>% mutate(pos = cumsum(count) - (0.5 * count), 
                                             count = ifelse(count == 0, NA, count))

p <- ggplot(pdat, aes(Year, count, fill = Organization)) + THEME + FILL +
       geom_bar(stat = "identity", position = "stack") +
       geom_text(aes(label = count, y = pos), size = 3, color = "white") + 
       theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
       labs(x = "Year", y = "Number of reports")
#ggsave("figures/coverage.png", p, width = 1.5 * w, height = h)

## Absolute wordcount by organization
dldat <- summarize(wc, nwords = sum(word_count))
p <- ggplot(dldat, aes(x = Year, y = nwords, color = Organization,
                       shape = Organization)) + THEME + COLOR +
        geom_line() +
        geom_point() +
        ylab("Number of words")
#ggsave("figures/org_wordcounts.png", p, width = w, height = h)

## Average document length by organization
adldat <- summarize(wc, nwords = mean(word_count))
p <- ggplot(adldat, aes(x = Year, y = nwords, color = Organization,
                       shape = Organization)) + THEME + COLOR +
        geom_line() +
        geom_point() +
        ylab("Average document length (words)")
#ggsave("figures/org_av_doclength.png", p, width = w, height = h)


## Get 'attention' by organization (word count, normalized by total wordcount in
## organization - year)
wc$Attention <- NA
for (i in 1:nrow(dldat)) {
    idx <- (wc$Organization == dldat$Organization[i] & wc$Year == dldat$Year[i])
    wc$Attention[idx] <- wc$word_count[idx]/dldat$nwords[i]
}

# Code for single country time series in attention ( by organization )
cstudy <- filter(wc, Country == "Iran, Islamic Republic of")
p <- ggplot(cstudy, aes(x = Year, y = Attention, color = Organization,
                        shape = Organization)) +
       COLOR + THEME + geom_line() + geom_point()
#ggsave("figures/attention_iraq.png", p, width = w, height = h)

## Bring in the coded variables
latrep <- read.table("../latent_repression.csv", sep = ",", header = TRUE)
latrep <- tbl_df(latrep)
ciri_emp <- read.table("../ciri_empowerment.csv", sep = ",", header = TRUE)
ciri_emp <- tbl_df(ciri_emp)

latrep <- rename(latrep, country_cow = COW, Year = YEAR)
ciri_emp <- rename(ciri_emp, country_cow = COW, Year = YEAR)
## match on cow code
wcj <- left_join(wc, latrep)
wcj <- left_join(wcj, ciri_emp)
#==============================================================================
# Plot attention by organizations to respect categories
#==============================================================================

### With Fariss's measure

## assign to respect bins
q <- quantile(wcj$latentmean, c(0, 0.25, 0.5, 0.75, 1), na.rm = TRUE)
wcj$Respect <- cut(wcj$latentmean, q, include.lowest = TRUE)
wcj$Respect <- as.character(wcj$Respect)
wcj$Respect[is.na(wcj$Respect)] <- "Not applicable"
wcj$Respect <- as.factor(wcj$Respect)
wcj$Respect <- factor(wcj$Respect, levels(wcj$Respect)[c(4, 2, 1, 3, 5)])
# plot attention by organization and respect category
wcj <- group_by(wcj, Organization, Year, Respect) %>%
       rename(Latent_Respect = Respect)
pdat <- summarize(wcj, Attention = sum(Attention))
p <- ggplot(pdat, aes(x = Year, y = Attention, color = Latent_Respect,
                      shape = Latent_Respect)) + THEME + COLOR + 
       geom_line() +
       geom_point() +
       facet_wrap(~ Organization, scales = "fixed")
#ggsave("figures/attention_fariss.png", p, width = w, height = h)

### With the state measure
wcj <- group_by(wcj, Organization, Year, State)
pdat <- summarize(wcj, Attention = sum(Attention))
pdat$State[is.na(pdat$State)] <- "Not applicable"
pdat$State <- as.factor(pdat$State)
p <- ggplot(pdat, aes(x = Year, y = Attention, color = State,
                      shape = State)) + THEME + COLOR + 
       geom_line() +
       geom_point() + 
       facet_wrap(~ Organization, scales = "fixed")
#ggsave("figures/attention_state.png", p, width = w, height = h)


### Make document name df for python tdm
out <- group_by(wcj) %>% select(filename, Organization, (DISAP:Latent_Respect))
write.csv(out, "../fnames_codings.csv",  row.names = FALSE) 
## write.csv(wcj, "../report_info.csv",  row.names = FALSE)

