# Exclude speaker ID
A01M0056="S05M0613 R00M0187 D01M0019 D04M0056 D02M0028 D03M0017"

# Evaluation set ID
eval1="A01M0110 A01M0137 A01M0097 A04M0123 A04M0121 A04M0051 A03M0156 A03M0112 A03M0106 A05M0011"
eval2="A01M0056 A03F0072 A02M0012 A03M0016 A06M0064 A06F0135 A01F0034 A01F0063 A01F0001 A01M0141"
eval3="S00M0112 S00F0066 S00M0213 S00F0019 S00M0079 S01F0105 S00F0152 S00M0070 S00M0008 S00F0148"

# move
ind=data/indiv
outd=data/indiv_other
mkdir -p $outd/eval/eval{1,2,3}
mkdir -p $outd/excluded

for list in $A01M0056 ; do
    find $ind -type d -name $list | xargs -i mv {} $outd/excluded
done

for list in $eval1 ; do
    find $ind -type d -name $list | xargs -i mv {} $outd/eval/eval1
done

for list in $eval2 ; do
    find $ind -type d -name $list | xargs -i mv {} $outd/eval/eval2
done

for list in $eval3 ; do
    find $ind -type d -name $list | xargs -i mv {} $outd/eval/eval3
done

# combine
ind=data/indiv_other
outd=data
# utils/data/combine_data.sh $outd/eval1 $ind/eval/eval1/*
# utils/data/combine_data.sh $outd/eval2 $ind/eval/eval2/*
# utils/data/combine_data.sh $outd/eval3 $ind/eval/eval3/*
ind=data/indiv
utils/data/combine_data.sh $outd/train $ind/*

