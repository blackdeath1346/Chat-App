#include<stdio.h>
int main()
{
int a[10],b[10],i,j,count=-1,count2=-1;
for(i=0;i<10;i++)
	{
	printf("enter value: ");
	scanf("%d",&a[i]);
	b[i]=a[i];
	}
for(i=0;i<10;i++)
	{
	for(j=(i+1);j<10;j++)
		{
		if((b[i]==b[j])&&b[j]!=-1)
		{
		count=count+1;
		b[j]=-1;
		}
		
		}
	if(b[i]!=-1)
		{
		count2=count2+1;
		}
	}
int c[count2+1],count3=-1;
for(i=0;i<10;i++)
{
    if(b[i]!=-1)
    {
        count3=count3+1;
        c[count3]=a[i];
    }
}
printf("number of duplicate elements is %d\n",(9-count2));
printf("forward array:\n");
for(i=0;i<=count2;i++)
	printf("%d\n",c[i]);
int d[count2+1];
for(i=0;i<=count2;i++)
{
    d[i]=c[count2-i];   
}
printf("reverse array:\n");
for(i=0;i<=count2;i++)
{
    printf("%d\n",d[i]);
}
}

