# Library
library(fmsb)

###plot 1###
# Create data: note in High school for Jonathan:
data=as.data.frame(matrix( sample( 2:20 , 10 , replace=T) , ncol=10))
colnames(data)=c("math" , "english" , "biology" , "music" , "R-coding", "data-viz" , "french" , "physic", "statistic", "sport" )

# To use the fmsb package, I have to add 2 lines to the dataframe: the max and min of each topic to show on the plot!
data=rbind(rep(20,10) , rep(0,10) , data)

# The default radar chart proposed by the library:
radarchart(data)

###plot 2###
data=as.data.frame(matrix( sample( 0:2 , 9 , replace=T) , ncol=9))
colnames(data)=c("Lactose" , "Vitamin E" , "Vitamin D" , "Vitamin A" , "Vitamin B12", "Calcium" , "Iron" , "folic acid", "Caffeine")

# To use the fmsb package, I have to add 2 lines to the dataframe: the max and min of each topic to show on the plot!
data=rbind(rep(2,9) , rep(0,9) , data)

# The default radar chart proposed by the library:
radarchart(data)

radarchart( data  , axistype=1 , 

            #custom polygon
            pcol=rgb(0.2,0.5,0.5,0.9), plwd=4 , 

            #custom the grid
            cglcol="grey", cglty=1, axislabcol="grey", caxislabels=seq(0,2,0.5), cglwd=0.8,

            #custom labels
            vlcex=0.8 
)

#ref to: http://www.r-graph-gallery.com/142-basic-radar-chart/
