



work_dir <- 'C:/Users/Yarden-/Documents/Import plot stocks R script' 
setwd(work_dir)






########## url_to_df - return a data table from a url string ##########
url_to_df <- function(url_str,
                      percent_format_columns = NULL) {
  # check that 'RCurl', 'XML' packages are loaded
  if (sum(c("RCurl", "XML") %in% loadedNamespaces() != c(T, T)) > 0) {
    stop('RCurl and XML packages not detected. Please load packages or install then load.')
  }
  
  # check that url_str is a string
  if (!is.character(url_str)) {
    stop("url_str should be a character string indicating the dataframe's url")
  }
  
  # get the html code from url_str
  html_text <- getURL(url_str, .encoding = 'UTF-8')  # get html code as text
  
  ## get the 3rd table, which contains the data
  ## also, clean the html source code, which is badly written
  # seperate the code, so that it contains only the third <table> tag
  start_tag <- '<table'
  end_tag <- '</table>'
  split_text <- strsplit(html_text, start_tag)[[1]][4]  # keeps the last table tag
  split_text <- strsplit(split_text, end_tag)[[1]][1]  # throws away everything after
  # put together everything with the seperating tags
  table_text <- paste(start_tag, split_text, end_tag, sep='')
  
  # correct the html code, add the <tr> tags, missing in the original html source code
  table_text_fixed <- gsub("</tr><td>", "</tr><tr><td>", table_text, fixed = TRUE)
  
  ## convert html code into a table
  # header is F, because otherwise the Hebrew UTF-8 encoding is screwed up
  stock_raw <- readHTMLTable(table_text_fixed, header=F,
                             stringsAsFactors=F, which = 1, encoding = "UTF-8")
  
  # correct col and row names, get them from first col and row
  stock_raw <- as.data.frame(stock_raw)
  row_saved_names <- stock_raw[-1,1]  # save row names
  stock_raw <- stock_raw[,-1]
  
  column_saved_names <- stock_raw[1,]  # replace col names
  colnames(stock_raw) <- column_saved_names
  stock_raw <- stock_raw[-1,]  # remove first row, which is "header"
  
  
  # correct data formatting for character containing percent symbol
  if (is.null(percent_format_columns)){
  percent_format_columns <- c('מרחק מגבוה 52 שבועות %',
                              '% מרחק מנמוך 52 שבועות',
                              '% תשואה מתחילת החודש',
                              '% תשואה 3 חודשים אחרונים',
                              '% תשואה מתחילת השנה',
                              '% תשואה 12 חודשים אחרונים')
  }
  
  
  for (column in percent_format_columns) {
    stock_raw[, column] <- as.numeric(
      gsub("%", "",stock_raw[, column]))/100
  }
  
  
  # correct data type to numeric instead of factor/character, remove commas in numbers
  stock_raw <- as.data.frame(apply(stock_raw, 2,
                                   FUN=function(x) as.numeric(gsub(",", "", x))),
                             row.names = row_saved_names,
                             na.strings = c('N/A', 'N/A%', '999999'))
  
  return(stock_raw)
  
  ########## url_to_df function preformance checks ##########
  # url_str <- 'http://www.calcalist.co.il/Ext/Comp/I-Invest/StockFilter/StockExcel/1,15654,1-29-9-2*MARKET_VALUE*desc*829371*0,00.xls?minmax=0.56:192525:0.16:321.1:-3030:1695:-999999:62.3&anaf=%D7%9B%D7%9C%20%D7%94%D7%A2%D7%A0%D7%A4%D7%99%D7%9D&hideParams='
  # stocks_data <- url_to_df(url_str)
  # 
  # sapply(stocks_data, mode)
  # sapply(stocks_data, is.factor)
  # sapply(stocks_data, is.numeric)
  # 
  # str(stocks_data)
  # head(stocks_data)
  # head(stocks_data[,1])
  # row.names(stocks_data)
  # row.names(stocks_data[1,])
  # colnames(stocks_data[1,])
  # colnames(stocks_data)
  # stocks_data['פועלים','תשואה על ההון העצמי']
  # 
  # temp_stock <- stocks_data[-which(row.names(stocks_data) == 'סאני'),]
  # plot(log(temp_stock[,1]), temp_stock[,3])
  # plot(temp_stock[,1], temp_stock[,3])

}










########## get a correct data url path (to "export to excel") ##########
get_init_data_url <- function(stock_screener_url = 'http://www.calcalist.co.il/stocks/home/0,7340,L-4021,00.html',
                              sleep_time_1 = 1,
                              sleep_time_2 = 0.5,
                              sleep_time_3 = 4) {
  # require(rJava)
  # require(devtools)
  # install_github('seleniumJars', 'LluisRamon')
  # install_github('relenium', 'LluisRamon')
  
  ## init browser
  firefox <- firefoxClass$new()  # browser
  firefox$get(stock_screener_url)  # open stock screener url
  
  # sleep for a few seconds, let page load and ads to go away
  Sys.sleep(sleep_time_1)
  
  ## click to remove all parameters except market cap
  # this allows the list to be complete (in terms of the number of companies)
  # it also generates NA's (which is ok...)
  firefox$findElementByXPath('//*[@id="stock_filter_2"]/div/a')$click()  # close parameter number 2 (EPS)
  firefox$findElementByXPath('//*[@id="stock_filter_9"]/div/a')$click()  # close parameter number 9 (ROE)
  firefox$findElementByXPath('//*[@id="stock_filter_29"]/div/a')$click()  # close parameter number 29 (P/E)
  Sys.sleep(sleep_time_2)
  
  ## click on show results button
  # more info : http://www.rdocumentation.org/packages/relenium/versions/0.3.0/topics/webElementClass?
  firefox$findElementByXPath('//*[@id="AmountSection"]/div/div/div/a')$click()
  
  # sleep for a while, let the data table get populated
  Sys.sleep(sleep_time_3)
  
  # copy "excel" data link address
  excel_link <- firefox$findElementByXPath('//*[@id="StockResultsArea"]/div[4]/a[2]')$getAttribute(stringName = 'href')
  # gets:    javascript:SendPrintAndExel('/Ext/Comp/I-Invest/StockFilter/StockExcel/1,15654,1-29-9-2*MARKET_VALUE*desc*831267*numanaf,00.xls?minmax=replaceminmax&anaf=repanaf&hideParams=REPLACEHIDEPARAMS',%20'excel',%200,%20'SelectTitle')
  # convert to: http://www.calcalist.co.il/Ext/Comp/I-Invest/StockFilter/StockExcel/1,15654,1-29-9-2*MARKET_VALUE*desc*831273*0,00.xls?minmax=0.56:196177:0.16:277.3:-3030:1695:-999999:62.3&anaf=%D7%9B%D7%9C%20%D7%94%D7%A2%D7%A0%D7%A4%D7%99%D7%9D&hideParams=
  # this works: http://www.calcalist.co.il/Ext/Comp/I-Invest/StockFilter/StockExcel/1,15654,1-29-9-2*MARKET_VALUE*desc*831267*numanaf,00.xls?minmax=replaceminmax&anaf=repanaf&hideParams=REPLACEHIDEPARAMS
  
  #close connection when done
  firefox$close()
  
  ## convert excel link to data url
  start_tag <- "javascript:SendPrintAndExel"
  end_tag <- "',%20'excel',%200,%20'SelectTitle')"
  html_data_link <- strsplit(excel_link, start_tag)[[1]][2]  # splits the text
  html_data_link <- substring(html_data_link, 3) # remove first 3 strings
  html_data_link <- strsplit(html_data_link, end_tag)[[1]]  # throws away everything after
  
  # put together everything with the seperating tags
  html_data_link <- paste('http://www.calcalist.co.il', html_data_link, sep='')
  
  return(html_data_link)

}








########## replace Hebrew column names with English column names ##########
translate_var_names <- function(stocks_data,
                                nn = cbind(old = c("שווי שוק",
                                                   "EPS-רווח למניה",
                                                   "רווח גולמי למכירות",
                                                   "רווח תפעולי למכירות",
                                                   "רווח לפני מס למכירות",
                                                   "רווח נקי למכירות",
                                                   "תשואה על ההון העצמי",
                                                   "תשואה על ההשקעה",
                                                   "תשואה על הנכסים",
                                                   "דיבידנט למניה",
                                                   "תשואות דיבידנט",
                                                   "מרחק מגבוה 52 שבועות %",
                                                   "% מרחק מנמוך 52 שבועות",
                                                   "בטא",
                                                   "סטיית תקן",
                                                   "% תשואה מתחילת החודש",
                                                   "% תשואה 3 חודשים אחרונים",
                                                   "% תשואה מתחילת השנה",
                                                   "% תשואה 12 חודשים אחרונים",
                                                   "מכפיל תזרים",
                                                   "מכפיל הון",
                                                   "מכפיל מכירות",
                                                   "הון עצמי למאזן",
                                                   "יחס שוטף",
                                                   "מנוף פיננסי",
                                                   "מכפיל רווח"),
                                           
                                           new = c('market_cap',
                                                   'EPS',
                                                   'gross_margin',
                                                   'operating_margin',
                                                   'pre-tax_profit_margin',
                                                   'net_profit_margin',
                                                   'ROE',
                                                   'ROI',
                                                   'ROA',
                                                   'dividend_per_share',
                                                   'dividend_yield',
                                                   '%_from_52_week_high',
                                                   '%_from_52_week_low',
                                                   'beta',
                                                   'standard_dev',
                                                   'return_this_month',
                                                   'trailing_3_month_return',
                                                   'return_this_year',
                                                   'trailing_12_month_return',
                                                   'price_to_cashflow',
                                                   'price_to_book',
                                                   'price_to_revenues',
                                                   'bv_to_assets',
                                                   'cur_assets_to_cur_liab',
                                                   'liab_to_bv',
                                                   'PE'))
) {
  # given var names
  var_names <- colnames(stocks_data)
  
  # check that var names match expected var names
  if (!all.equal(nn[,'old'], var_names)) {
    stop('Unrecognized variable names, please check the column names')
  }
  
  # match and replace column names
  ii <- match(nn[,"old"], var_names)
  names(stocks_data)[ii] <- nn[,"new"]
  
  return(stocks_data)
  
}









########## parameter structure ##########
# work with a list
# http://stackoverflow.com/questions/10678872/equivalent-of-a-python-dict-in-r
# http://stackoverflow.com/questions/2858014/working-with-dictionaries-lists-in-r
# 
## div/share cuts down significantly, for some reason
## earnings cut down by a few, maybe not a problem 
# 2 EPS - רווח למניה
# 5 רווח גולמי למכירות  
# 6 רווח תפעולי למכירות  
# 7 רווח לפני מס למכירות  
# 8 רווח נקי למכירות  
# 9 ROE - תשואה על ההון העצמי  
# 12 ROI - תשואה על ההשקעה  
# 14 ROA - תשואה על הנכסים  
# 17 דיבידנד למניה  
# 18 תשואת דיבידנד 
# 
## dist from 52 weeks low/high cuts a few (why??)
## beta, stdev are ok
# 19 % מרחק מגבוה 52 שבועות  
# 20 % מרחק מנמוך 52 שבועות  
# 21 בטא  
# 22 סטיית תקן 
# 
## return of last 12 months/begin of year cuts a few
# 23 % תשואה מתחילת החודש  
# 24 % תשואה 3 חודשים אחרונים  
# 25 % תשואה מתחילת השנה  
# 26 % תשואה 12 חודשים אחרונים 
# 
## cashflow multi, p/e multi cuts quite a few
## p/bv is ok, sales multi cuts a few (some cut as with earning figs)
# 27 מכפילי תזרים  
# 30 מכפיל הון  
# 29 P/E - מכפיל רווח  
# 28 מכפיל מכירות 
# 
## equity/ assets is ok
## quick ratio cuts dow a few, financial lev cuts down a bunch
# 31 הון עצמי למאזן  
# 34 יחס שוטף  
# 35 מנוף פיננסי 


#### plotting tips
# http://docs.ggplot2.org/0.9.3.1/geom_point.html
# http://www.showmeshiny.com/
# https://github.com/jcheng5/crosstalk-demo?files=1
# https://beta.rstudioconnect.com/jcheng/shiny-crosstalk/







########## running commands ##########
## import libraries
library(relenium)  # firefoxClass, More info: https://github.com/LluisRamon/relenium
library(XML)  # readHTMLTable
library(RCurl)  # getURL

## get the correct data url
data_url <- get_init_data_url()

## edit the data url path to get the full-data url
complete_data_url <- gsub('1*MARKET',
                          '1-2-5-6-7-8-9-12-14-17-18-19-20-21-22-23-24-25-26-27-30-28-31-34-35-29*MARKET',
                          data_url, fixed = TRUE)

## get data full-data from website
stocks_data <- url_to_df(complete_data_url)

## change column names to English column names
trans_stocks_data <- translate_var_names(stocks_data)

## save to file
saveRDS(trans_stocks_data, file = 'stocks_data.rds')

#####################################################################