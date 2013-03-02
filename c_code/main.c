/*
	Autor Livio Conzett
 
	22.11.2011
 */ 


#include <stdio.h>

#define X	4 //player
#define O	1 //PC
#define S	0 //nothing
#define SUM(x,y,z) (field[x]+field[y]+field[z])


int find_line(int sum,int *a,int *b,int *c);
int check_line(int x,int y,int z,int sum,int *a,int *b,int *c);
int ran (int a, int b, int c, int d, int max);
int checkwin (int zero, int one, int two, int three, int four, int five, int six, int seven, int eight);
int compmove (void);
int clearfield(void);




int field[9];
int done = 0;
int won = 0;


int main (int zero, int one, int two, int three, int four, int five, int six, int seven, int eight){

	int playermove=0;
	
	field[0] = six;
	field[1] = seven,
	field[2] = eight;
	field[3] = three;
	field[4] = four;
	field[5] = five;
	field[6] = zero;
	field[7] = one;
	field[8] = two;
	
	compmove();

	
	if(field[0]!= six){
		playermove = 6;
	}
	
	if(field[1]!= seven){
		playermove = 7;
	}	
	
	if(field[2]!= eight){
		playermove = 8;
	}
	
	if(field[3]!= three){
		playermove = 3;
	}
	
	if(field[4]!= four){
		playermove = 4;
	}
	
	if(field[5]!= five){
		playermove = 5;
	}

	if(field[6]!= zero){
		playermove = 0;
	}
	
	if(field[7]!= one){
		playermove = 1;
	}
	
	if(field[8]!= two){
		playermove = 2;
	}
	
	//checkwin (1, 4, 1, 4, 1, 4, 4, 1, 0);
	clearfield();
	return playermove;
	
}

int ran (int a, int b, int c, int d, int max){
	
	srand(time(NULL));
	int z=0;
	
	z = (rand() %max);
	
	if(z == a)return a;
	if(z == b)return b;
	if(z == c)return c;
	if(z == d)return d;
	
	return 0;
}



int find_line(int sum,int *a,int *b,int *c) {
	if(check_line(0,1,2,sum,a,b,c)) return 1;
	if(check_line(3,4,5,sum,a,b,c)) return 1;
	if(check_line(6,7,8,sum,a,b,c)) return 1;
	if(check_line(0,3,6,sum,a,b,c)) return 1;
	if(check_line(1,4,7,sum,a,b,c)) return 1;
	if(check_line(2,5,8,sum,a,b,c)) return 1;
	if(check_line(0,4,8,sum,a,b,c)) return 1;
	if(check_line(2,4,6,sum,a,b,c)) return 1;
	return 0;
}


int check_line(int x,int y,int z,int sum,int *a,int *b,int *c) {
	if(field[x]+field[y]+field[z]!=sum) return 0;
	if(SUM(x,y,z)!=sum) return 0;
	*a=x; *b=y; *c=z;
	return 1;

}

int checkwin (int zero, int one, int two, int three, int four, int five, int six, int seven, int eight) {
	int a,b,c;
	
	field[0] = six;
	field[1] = seven,
	field[2] = eight;
	field[3] = three;
	field[4] = four;
	field[5] = five;
	field[6] = zero;
	field[7] = one;
	field[8] = two;
	won=0;
	
	printf("%d,%d,%d,%d,%d,%d,%d,%d,%d\n", zero, one, two, three, four, five, six, seven, eight);
	
	if(find_line(X+X+X,&a,&b,&c)) {
		won = 14;
		printf("You just got lucky");
		clearfield();
		return  14;
	}
	if(find_line(O+O+O,&a,&b,&c)) {
		won = 11;
		printf("I won, bitches!");
		clearfield();
		return 11;
	}
  /*for(a=0,b=0;a<9;a++) if(field[a]==S) b=1;
	if(b==0) {
		won=10;
		printf("No one wins");
	}*/
	
	for(a=0,b=0;a<9;a++) if(field[a]==S) b++;
	if(b==1) {
		won=10;
		printf("No one wins haha");
		clearfield();
		return 10;
    }
	
	clearfield();
	//return won;
	return 0;
}


int compmove (void){
	
	int a,b,c;
	int e;
	
//check for his win
	
	if(find_line(O+O+S, &a, &b, &c)){
		if(field[a]==S)return field[a]=O;
		if(field[b]==S)return field[b]=O;
		if(field[c]==S)return field[c]=O;
	}
	
//check for player win
	
	if(find_line(X+X+S, &a, &b, &c)){
		if(field[a]==S)return field[a]=O;
		if(field[b]==S)return field[b]=O;
		if(field[c]==S)return field[c]=O;
	}
	
//check for bad move one.
	
	if(field[6]+field[4]+field[2] == X+O+X) return field[ran(1,3,5,7,7)]=O;
	
//Zecevic corner
	
	if(field[7]+field[5]==X+X){
		return field[8]=O;
	}
	
	if(field[7]+field[3]==X+X){
		return field[6]=O;
	}
	
	if(field[3]+field[1]==X+X){
		return field[0]=O;
	}
	
	if(field[1]+field[5]==X+X){
		return field[2]=O;
	}
	
	
//check for line with one O
	
	if(find_line(O, &a, &b, &c)){
		if(field[a]==S) return field[a]=O;
		if(field[b]==S) return field[b]=O;
		if(field[c]==S) return field[c]=O;
	}
//check for middle taken?
	
	if(field[1]==X || field[3]==X || field[5]==X || field [7]==X) return field[4]=O;
	
	
//check for middle taken?
	
	if(field[4]==X) return field[ran(0, 2, 6, 8, 8)]=O;
	
	
//check for make trap.
	
	if(field[0]==O && field[4]==X && field[8]==S) return field[8]=O;	
	if(field[2]==O && field[4]==X && field[6]==S) return field[6]=O;
	if(field[6]==O && field[4]==X && field[2]==S) return field[2]=O;
	if(field[8]==O && field[4]==X && field[0]==S) return field[0]=O;
	
	
//check for take middle
	
	if(field[4]==S) return field[4]=O;
	
//else take open field
	else {
		for(e=0;e<9;e++){
		
			if (field[e]==S) {
				return field[e]=O;
			}
			
		
		}
	}

	
	
	return 0;
}


int clearfield (void){

int i;
	
	for(i=0;i<9;i++){
		
		field[i] = S;
		
	}
	

	return 0;
}

