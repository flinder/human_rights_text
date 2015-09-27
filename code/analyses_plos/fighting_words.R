## =============================================================================
## Get the most important words per human rights category with Monroe et al's stuff
## =============================================================================

library(doParallel)
library(xtable)

# ++++++++++++++++++++
# CONFIG
# ++++++++++++++++++++

TABLE_DIR <- "../../HR_Text/HR_texts_03/miw_tables.tex"
DTM_DIR <- "../../data/dtms/aggregated/dtm_red_"
measures <- c("amnesty", "disap", "hathaway", "kill", "polpris", "state", "tort",
              "assn", "formov", "dommov", "speech", "elecsd", "new_relfre", "worker")
files <- paste0(DTM_DIR, measures, ".csv")


## Log odds ratio for word w in group i (applied once to each row)
lor <- function(row, a, a0, a0i, y, N) {
    log((row + a) / (sum(row) + a0i - row - a)) - log((y + a) / (N + a0 - y - a))    
}

vars <- function(row, a, y) 1/(row + y + 2 * a)

## Function to do the calculations on one dtm
get_fw <- function(dtm, var_corr = TRUE, a0) {

    cat("Calculate summaries\n")
    N <- sum(dtm)
    n <- rowSums(dtm)
    y <- colSums(dtm)
    a <- (a0 * y) / N
    a0i <- a0 * n / N
    cat("Calculate weights\n")
    weights <- list()
    for(i in 1:nrow(dtm)) {
        weights[[i]] <- lor(dtm[i, ], a, a0, a0i[i], y, N)
    }
    weights <- do.call(cbind, weights)
    #weights <- apply(dtm, 1, lor, a, a0, y, N)
    out <- weights
    
    if(var_corr){
        cat("Calculate Variances\n")
        vars <- apply(dtm, 1, vars, a, y)
        out <- weights / vars
    }
    #rownames(out) <- colnames(dtm)
    #colnames(out) <- rownames(dtm)
    return(out)

}

## Load files
dtms <- vector(mode = "list", length = length(files))
for(i in 1:length(files)) {
  cnames <- unlist(strsplit(readLines(files[i], n = 1, encoding = "UTF-8"), ","))
  nc <- length(cnames)
  cont <- scan(files[i], what = integer(), skip = 1, sep = ",")
  dtms[[i]] <- matrix(cont, nc = nc, byrow = TRUE)
  colnames(dtms[[i]]) <- cnames
  rownames(dtms[[i]]) <- seq(1:nrow(dtms[[i]]))
}

log_odds <- lapply(dtms, get_fw, a0 = 1000, var_corr = TRUE)
names(log_odds) <- measures


## =============================================================================
## Extract and visualize resutls


## Make Tables of most important words per category
extMiw <- function(df, n){
    ncat <- ncol(df)
    out <- matrix(NA, nc = ncat, nr = n)
    colnames(out) <- as.character(c(1:ncat))
    for(i in 1:ncat){
        h_idx <- order(df[, i], decreasing = TRUE)[1:n]
        out[, i] <- rownames(df)[h_idx]
    }
    return(out)
}

n <- 10
miw <- lapply(log_odds, extMiw, n)
names(miw) <- measures

## Reorder and relable ciri tables
ciri <- names(miw)[-c(1, 3, 6)]
for(nam in ciri){
    df <- miw[[nam]]
    miw[[nam]] <- df[, c(3, 2, 1)]
    colnames(miw[[nam]]) <- c(2, 1, 0)
}

caps <- c("PTS (Amnesty International)", "CIRI Disappearance", "Hathaway",
          "CIRI Extrajudical Killing", "CIRI Political Imprisonment",
          "PTS (State Department)", "CIRI Torture",
          "CIRI Freedom of Assembly and Association",
          "CIRI Freedom of Foreign Movement and Travel",
          "CIRI Freedom of Domestic Movement", "CIRI Freedom of Speech and Press",
          "CIRI Electoral Self-determination", "CIRI Freedom of Religion",
          "CIRI Worker Rights")

for(i in 1:length(miw)){
  cap <- paste0(n, " most important words for ", caps[i], " categorization.")
  tab <- xtable(miw[[i]], caption = cap)
  print(tab, type = "latex", file = TABLE_DIR, 
        append = TRUE, include.rownames=FALSE)
}

