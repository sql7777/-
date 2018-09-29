
#include<stdio.h> 
#include<stdlib.h> 
#include<unistd.h> 
#include<sys/types.h> 
#include<sys/stat.h> 
#include<fcntl.h> 
#include<termios.h> 
#include<errno.h> 
#include<string.h>

#define FALSE -1
#define TRUE 0

extern "C" {
	//int UART_Open(int fd, char* port);
	int UART_OpenCom(int fd, char* port,int speed);
	void UART_Close(int fd);
	//int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity);
	//int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity);
	int UART_Recv(int fd, char *rcv_buf, int data_len);
	int UART_Recv_nowait(int fd, char *rcv_buf, int data_len);
	int UART_Recv_Main(int fd, char *rcv_buf, int data_len, int s, int ms);
	int UART_Send(int fd, char *send_buf, int data_len);
}
int UART_Open(int fd, char* port);
int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity);
int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity);
/*****************************************************************
* 名称： UART0_Open
* 功能： 打开串口并返回串口设备文件描述
* 入口参数： fd :文件描述符 port :串口号(ttyS0,ttyS1,ttyS2)
* 出口参数： 正确返回为1，错误返回为0
*****************************************************************/
int UART_Open(int fd, char* port)
{

	fd = open(port, O_RDWR | O_NOCTTY | O_NDELAY);
	//fd = open(port, O_RDWR | O_NONBLOCK);
	if (FALSE == fd) {
		perror("Can't Open Serial Port");
		return(FALSE);
	}

	//判断串口的状态是否为阻塞状态 
	if (fcntl(fd, F_SETFL, 0) < 0) {
		printf("fcntl failed!\n");
		return(FALSE);
	}
	else {
		//    printf("fcntl=%d\n",fcntl(fd, F_SETFL,0));
	}

	//测试是否为终端设备
	if (0 == isatty(STDIN_FILENO)) {
		printf("standard input is not a terminal device\n");
		return(FALSE);
	}

	return fd;
}

void UART_Close(int fd)
{
	close(fd);
}

/*******************************************************************
* 名称： UART0_Set
* 功能： 设置串口数据位，停止位和效验位
* 入口参数： fd 串口文件描述符
* speed 串口速度
* flow_ctrl 数据流控制
* databits 数据位 取值为 7 或者8
* stopbits 停止位 取值为 1 或者2
* parity 效验类型 取值为N,E,O,,S
*出口参数： 正确返回为1，错误返回为0
*******************************************************************/
int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity)
{

	int i;
	//    int status; 
	int speed_arr[] = { B38400, B19200, B9600, B4800, B2400, B1200, B300,
		B38400, B19200, B9600, B4800, B2400, B1200, B300
	};
	int name_arr[] = {
		38400, 19200, 9600, 4800, 2400, 1200, 300, 38400,
		19200, 9600, 4800, 2400, 1200, 300
	};
	struct termios options;// , oldtio;
	/*保存测试现有串口参数设置，在这里如果串口号等出错，会有相关的出错信息*/      
	//if (tcgetattr(fd, &oldtio) != 0)
	//{ 
	//	perror("SetupSerial 1");	
	//	printf("tcgetattr( fd,&oldtio) -> %d\n", tcgetattr(fd, &oldtio));      
	//	return -1;
	//}

	/*tcgetattr(fd,&options)得到与fd指向对象的相关参数，并将它们保存于options,该函数,还可以测试配置是否正确，该串口是否可用等。若调用成功，函数返回值为0，若调用失败，函数返回值为1.
	*/
	//bzero(&options, sizeof(options));
	if (tcgetattr(fd, &options) != 0) {
		perror("SetupSerial 1");
		return(FALSE);
	}
	switch (speed)
	{
	case 2400:
		cfsetispeed(&options, B2400);
		cfsetospeed(&options, B2400);
		break;
	case 4800:
		cfsetispeed(&options, B4800);
		cfsetospeed(&options, B4800);
		break;
	case 9600:
		cfsetispeed(&options, B9600);
		cfsetospeed(&options, B9600);
		break;
	case 115200:
		cfsetispeed(&options, B115200);
		cfsetospeed(&options, B115200);
		//printf("Is that you\n");
		break;
	case 460800:
		cfsetispeed(&options, B460800);
		cfsetospeed(&options, B460800);
		break;
	default:
		cfsetispeed(&options, B9600);
		cfsetospeed(&options, B9600);
		break;
	}

	////设置串口输入波特率和输出波特率
	//for (i = 0; i < sizeof(speed_arr) / sizeof(int); i++) {
	//	if (speed == name_arr[i]) {
	//		cfsetispeed(&options, speed_arr[i]);
	//		cfsetospeed(&options, speed_arr[i]);
	//	}
	//}
	//printf("set_speed c i speed:%d\n", name_arr[i - 1]);
	//修改控制模式，保证程序不会占用串口        
	options.c_cflag |= CLOCAL;
	//修改控制模式，使得能够从串口中读取输入数据
	options.c_cflag |= CREAD;
	//设置数据流控制
	switch (flow_ctrl) {
	case 0: //不使用流控制
		options.c_cflag &= ~CRTSCTS;
		break;
	case 1: //使用硬件流控制
		options.c_cflag |= CRTSCTS;
		break;
	case 2: //使用软件流控制
		options.c_cflag |= IXON | IXOFF | IXANY;
		break;
	}
	//设置数据位
	options.c_cflag &= ~CSIZE; //屏蔽其他标志位
	switch (databits) {
	case 5:
		options.c_cflag |= CS5;
		break;
	case 6:
		options.c_cflag |= CS6;
		break;
	case 7:
		options.c_cflag |= CS7;
		break;
	case 8:
		options.c_cflag |= CS8;
		break;
	default:
		fprintf(stderr, "Unsupported data size\n");
		return (FALSE);
	}
	//设置校验位
	switch (parity) {
	case 'n':
	case 'N': //无奇偶校验位。
		options.c_cflag &= ~PARENB;   /* Clear parity enable */
		options.c_iflag &= ~INPCK;     /* Enable parity checking */
		options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); /*Input*/
		options.c_oflag &= ~OPOST;   /*Output*/
		break;
	case 'o':
	case 'O': //设置为奇校验 
		options.c_cflag |= (PARODD | PARENB);
		options.c_iflag |= INPCK;
		break;
	case 'e':
	case 'E': //设置为偶校验 
		options.c_cflag |= PARENB;
		options.c_cflag &= ~PARODD;
		options.c_iflag |= INPCK;
		break;
	case 's':
	case 'S': //设置为空格 
		options.c_cflag &= ~PARENB;
		options.c_cflag &= ~CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported parity\n");
		return (FALSE);
	}
	// 设置停止位 
	switch (stopbits) {
	case 1:
		options.c_cflag &= ~CSTOPB;
		break;
	case 2:
		options.c_cflag |= CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported stop bits\n");
		return (FALSE);
	}
//+++
	/* Set input parity option */
	if ((parity != 'n') && (parity != 'N'))
		options.c_iflag |= INPCK;

	options.c_cc[VTIME] = 1;//       5; // 0.5 seconds
	options.c_cc[VMIN] = 1;

	//options.c_cflag &= ~CRTSCTS;
	//options.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
	//options.c_iflag &= ~(BRKINT | ICRNL | IXON | ISTRIP);
	//options.c_oflag &= ~(OPOST);

	////+++
	//options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); /*Input*/
	//options.c_oflag &= ~OPOST;   /*Output*/
	////+++

	options.c_cflag &= ~HUPCL;
	options.c_iflag &= ~INPCK;
	options.c_iflag |= IGNBRK;
	options.c_iflag &= ~ICRNL;
	options.c_iflag &= ~IXON;
	options.c_lflag &= ~IEXTEN;
	options.c_lflag &= ~ECHOK;
	options.c_lflag &= ~ECHOCTL;
	options.c_lflag &= ~ECHOKE;
	options.c_oflag &= ~ONLCR;

	tcflush(fd, TCIFLUSH); /* Update the options and do it NOW */
	if (tcsetattr(fd, TCSANOW, &options) != 0)
	{
		perror("SetupSerial 3");
		return (FALSE);
	}
//+++
	////修改输出模式，原始数据输出
	//options.c_oflag &= ~OPOST;
	////设置等待时间和最小接收字符
	//options.c_cc[VTIME] = 1; /* 读取一个字符等待1*(1/10)s */
	//options.c_cc[VMIN] = 1; /* 读取字符的最少个数为1 */

	//						//如果发生数据溢出，接收数据，但是不再读取
	//tcflush(fd, TCIFLUSH);

	////激活配置 (将修改后的termios数据设置到串口中）
	//if (tcsetattr(fd, TCSANOW, &options) != 0)
	//{
	//	perror("com set error!/n");
	//	return (FALSE);
	//}
	return (TRUE);
}
int set_speed(int fd, int speed) {
	unsigned int   i;
	int speed_arr[] = { B38400, B19200, B9600, B4800, B2400, B1200, B300,
		B38400, B19200, B9600, B4800, B2400, B1200, B300
	};
	int name_arr[] = {
		38400, 19200, 9600, 4800, 2400, 1200, 300, 38400,
		19200, 9600, 4800, 2400, 1200, 300
	};
	int   status;
	struct termios   Opt;
	tcgetattr(fd, &Opt);
	for (i = 0; i < sizeof(speed_arr) / sizeof(int); i++) {
		if (speed == name_arr[i]) {
			tcflush(fd, TCIOFLUSH);
			cfsetispeed(&Opt, speed_arr[i]);
			cfsetospeed(&Opt, speed_arr[i]);
			printf("set_speed speed:%d\n", name_arr[i]);
			status = tcsetattr(fd, TCSANOW, &Opt);
			if (status != 0) {
				perror("tcsetattr fd1");
				return (FALSE);
			}
			tcflush(fd, TCIOFLUSH);
		}
	}
	printf("set_speed i speed:%d\n", name_arr[i-1]);
	return (TRUE);
}
int set_Parity(int fd, int databits, int stopbits, int parity)
{
	struct termios options;
	if (tcgetattr(fd, &options) != 0)
	{
		perror("SetupSerial 1");
		return(FALSE);
	}
	options.c_cflag &= ~CSIZE;
	switch (databits) /*设置数据位数*/
	{
	case 7:
		options.c_cflag |= CS7;
		break;
	case 8:
		options.c_cflag |= CS8;
		break;
	default:
		fprintf(stderr, "Unsupported data size\n");
		return (FALSE);
	}
	switch (parity)
	{
	case 'n':
	case 'N':
		//        options.c_cflag &= ~PARENB;   /* Clear parity enable */
		//        options.c_iflag &= ~INPCK;     /* Enable parity checking */
		options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); /*Input*/
		options.c_oflag &= ~OPOST;   /*Output*/
		break;
	case 'o':
	case 'O':
		options.c_cflag |= (PARODD | PARENB); /* 设置为奇效验*/
		options.c_iflag |= INPCK;             /* Disnable parity checking */
		break;
	case 'e':
	case 'E':
		options.c_cflag |= PARENB;     /* Enable parity */
		options.c_cflag &= ~PARODD;   /* 转换为偶效验*/
		options.c_iflag |= INPCK;       /* Disnable parity checking */
		break;
	case 'S':
	case 's': /*as no parity*/
		options.c_cflag &= ~PARENB;
		options.c_cflag &= ~CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported parity\n");
		return (FALSE);
	}
	/* 设置停止位*/
	switch (stopbits)
	{
	case 1:
		options.c_cflag &= ~CSTOPB;
		break;
	case 2:
		options.c_cflag |= CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported stop bits\n");
		return (FALSE);
	}
	/* Set input parity option */
	if ((parity != 'n') && (parity != 'N'))
		options.c_iflag |= INPCK;

	options.c_cc[VTIME] = 5; // 0.5 seconds
	options.c_cc[VMIN] = 1;

	options.c_cflag &= ~HUPCL;
	options.c_iflag &= ~INPCK;
	options.c_iflag |= IGNBRK;
	options.c_iflag &= ~ICRNL;
	options.c_iflag &= ~IXON;
	options.c_lflag &= ~IEXTEN;
	options.c_lflag &= ~ECHOK;
	options.c_lflag &= ~ECHOCTL;
	options.c_lflag &= ~ECHOKE;
	options.c_oflag &= ~ONLCR;

	tcflush(fd, TCIFLUSH); /* Update the options and do it NOW */
	if (tcsetattr(fd, TCSANOW, &options) != 0)
	{
		perror("SetupSerial 3");
		return (FALSE);
	}

	return (TRUE);
}
int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity)
{
	printf("UART_Init speed:%d\n", speed);
	//if (FALSE == set_speed(fd, speed))
	//{
	//	return FALSE;
	//}
	////UART_Init(fd, speed, 0, 8, 1, 'N');
	//if (FALSE == set_Parity(fd, databits, stopbits, parity))
	//{
	//	return FALSE;
	//}
	//else {
	//	return TRUE;
	//}
	//设置串口数据帧格式
	if (FALSE == UART_Set(fd, speed, flow_ctrlint, databits, stopbits, parity)) {
		return FALSE;
	}
	else {
		return TRUE;
	}
}



/*******************************************************************
* 名称： UART0_Recv
* 功能： 接收串口数据
* 入口参数： fd :文件描述符
* rcv_buf :接收串口中数据存入rcv_buf缓冲区中
* data_len :一帧数据的长度
* 出口参数： 正确返回为1，错误返回为0
*******************************************************************/
int UART_Recv_Main(int fd, char *rcv_buf, int data_len, int s, int ms)
{
	int len, fs_sel;
	fd_set fs_read;

	struct timeval time;

	FD_ZERO(&fs_read);
	FD_SET(fd, &fs_read);

	time.tv_sec = s;// 10;
	time.tv_usec = ms * 1000;

	//使用select实现串口的多路通信
	fs_sel = select(fd + 1, &fs_read, NULL, NULL, &time);
	if (fs_sel) {
		len = read(fd, rcv_buf, data_len);
		return len;
	}
	else {
		return FALSE;
	}
}


int UART_Recv(int fd, char *rcv_buf, int data_len)
{
	return UART_Recv_Main(fd, rcv_buf, data_len, 2, 0);
}
int UART_Recv_nowait(int fd, char *rcv_buf, int data_len)
{
	return UART_Recv_Main(fd, rcv_buf, data_len, 0, 1);
}

/*******************************************************************
* 名称： UART0_Send
* 功能： 发送数据
* 入口参数： fd :文件描述符
* send_buf :存放串口发送数据
* data_len :一帧数据的个数
* 出口参数： 正确返回为1，错误返回为0
*******************************************************************/
int UART_Send(int fd, char *send_buf, int data_len)
{
	int ret;

	ret = write(fd, send_buf, data_len);
	if (data_len == ret) {
		return ret;
	}
	else {
		tcflush(fd, TCOFLUSH);
		return FALSE;

	}

}


int UART_OpenCom(int fd, char* port, int speed)
{
	//int fd = FALSE;
	int ret;
	fd = UART_Open(fd, port);
	if (FALSE == fd) {
		printf("open error\n");
		return -1;
	}
	ret = UART_Init(fd, speed, 0, 8, 1, 'N');
	if (FALSE == ret) {
		UART_Close(fd);
		return -1;
	}
	if (FALSE == fd) {
		printf("Set Port Error\n");
		return -1;
	}
	return fd;
}
/*
int main(int argc, char **argv)
{
	int fd = FALSE;
	int ret;
	char rcv_buf[512];
	int i;
	if (argc != 2) {
		printf("Usage: %s /dev/ttySn \n", argv[0]);
		return FALSE;
	}
	fd = UART_Open(fd, argv[1]);
	if (FALSE == fd) {
		printf("open error\n");
		exit(1);
	}
	ret = UART_Init(fd, 115200, 0, 8, 1, 'N');
	if (FALSE == fd) {
		printf("Set Port Error\n");
		exit(1);
	}

	ret = UART_Send(fd, "*IDN?\n", 6);
	if (FALSE == ret) {
		printf("write error!\n");
		exit(1);
	}

	printf("command: %s\n", "*IDN?");
	memset(rcv_buf, 0, sizeof(rcv_buf));
	for (i = 0;; i++)
	{
		ret = UART_Recv(fd, rcv_buf, 512);
		if (ret > 0) {
			rcv_buf[ret] = '\0';
			printf("%s", rcv_buf);
		}
		else {
			printf("cannot receive data1\n");
			break;
		}
		if ('\n' == rcv_buf[ret - 1])
			break;
	}
	UART_Close(fd);
	return 0;
}
*/