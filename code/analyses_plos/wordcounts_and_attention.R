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

## Load wordcounts file (Extracted from mongoDB with extract_data.sh, replaced "'" with "" in file)
wc <- read.table("../../data/analyses_plos/all_reports.csv", sep = ",", header = TRUE)
wc <- tbl_df(wc)



wc <- rename(wc, year = year.0, fariss = fariss.mean) %>%
      group_by(organization, year)

## Coverage plot
counts <- summarise(wc, count = length(unique(country_name)))

pdat <- counts %>% group_by(year) %>% mutate(pos = cumsum(count) - (0.5 * count), 
                                             count = ifelse(count == 0, NA, count))

p <- ggplot(pdat, aes(year, count, fill = organization)) + THEME + FILL +
       geom_bar(stat = "identity", position = "stack") +
       geom_text(aes(label = count, y = pos), size = 3, color = "white") + 
       theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
       labs(x = "Year", y = "Number of reports")
#ggsave("figures/coverage.png", p, width = 1.5 * w, height = h)

## Absolute wordcount by organization
dldat <- summarize(wc, nwords = sum(wordcount))
p <- ggplot(dldat, aes(x = year, y = nwords, color = organization,
                       shape = organization)) + THEME + COLOR +
        geom_line() +
        geom_point() +
        ylab("Number of words")
#ggsave("figures/org_wordcounts.png", p, width = w, height = h)

## Average document length by organization
adldat <- summarize(wc, nwords = mean(wordcount))
p <- ggplot(adldat, aes(x = year, y = nwords, color = organization,
                       shape = organization)) + THEME + COLOR +
        geom_line() +
        geom_point() +
        ylab("Average document length (words)")
#ggsave("figures/org_av_doclength.png", p, width = w, height = h)


## Get 'attention' by organization (word count, normalized by total wordcount in
## organization - year)
wc$attention <- NA
for (i in 1:nrow(dldat)) {
    idx <- (wc$organization == dldat$organization[i] & wc$year == dldat$year[i])
    wc$attention[idx] <- wc$wordcount[idx]/dldat$nwords[i]
}

# Code for single country time series in attention ( by organization )
cstudy <- filter(wc, country_iso3c == "IRN")
p <- ggplot(cstudy, aes(x = year, y = attention, color = organization,
                        shape = organization)) +
       COLOR + THEME + geom_line() + geom_point()
#ggsave("figures/attention_iraq.png", p, width = w, height = h)


#==============================================================================
# Plot attention by organizations to respect categories
#==============================================================================

### With Fariss's measure

## assign to respect bins
q <- quantile(wc$fariss, c(0, 0.25, 0.5, 0.75, 1), na.rm = TRUE)
wc$respect <- cut(wc$fariss, q, include.lowest = TRUE)
wc$respect <- as.character(wc$respect)
wc$respect <- as.factor(wc$respect)
wc$respect <- factor(wc$respect, levels(wc$respect)[c(4, 2, 1, 3, 5)])
# plot attention by organization and respect category
wc <- group_by(wc, organization, year, respect) %>%
       rename(latent_respect = respect)
pdat <- summarize(wc, attention = sum(attention))
p <- ggplot(pdat, aes(x = year, y = attention, color = latent_respect,
                      shape = latent_respect)) + THEME + COLOR + 
       geom_line() +
       geom_point() +
       facet_wrap(~ organization, scales = "fixed")
#ggsave("figures/attention_fariss.png", p, width = w, height = h)

### With the state measure
wc <- group_by(wc, organization, year, state)
pdat <- summarize(wc, attention = sum(attention))
pdat$state[is.na(pdat$state)] <- "Not applicable"
pdat$state <- as.factor(pdat$state)
p <- ggplot(pdat, aes(x = year, y = attention, color = state,
                      shape = state)) + THEME + COLOR + 
       geom_line() +
       geom_point() + 
       facet_wrap(~ organization, scales = "fixed")
#ggsave("figures/attention_state.png", p, width = w, height = h)


### Make document name df for python tdm
## out <- group_by(wcj) %>% select(filename, Organization, (DISAP:Latent_Respect))
## write.csv(out, "../fnames_codings.csv",  row.names = FALSE) 
## write.csv(wcj, "../report_info.csv",  row.names = FALSE)

