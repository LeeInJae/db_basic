<!DOCTYPE html>
<%@page import = "java.sql.*"%>
<%@page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>

<meta http-equiv="Content-Type" content = "text/html; charset=UTF-8"/>
<html>
<head>
		<meta charset="utf-8"/>
		<title> Injae's Phone Book </title>
</head>

<body>
<%
request.setCharacterEncoding("UTF-8")
String addr = "jdbc:mysql://localhost/phouse";
String user = "popi";
String pw = "db1004";
Statement stmt;
Connection conn;

try{
	class.forName("com.mysql.jdbc.Driver");
}catch( ClassNotFoundException e)
{
	out.println("driver error");
	out.println(e.getMessage());
	return;
}
out.println("Driver Load OK");

conn = DriverManager.getConnection(add, user, pw);
out.println("Connection OK");

stmt = conn.createStatement();
String query = "create table ijbook(
					name varchar(20),
					phone varchar(20))"
stmt.execute(query);

String name = request.getParameterValues("이름")
StringBuffer  phone = new StringBuffer();
phone.append(request.getParameter("phone1"));
phone.append("-");
phone.append(request.getParameter("phone2"));
phone.append("-");
phone.append(request.getParameter("phone3"));

PreparedStatement pstmt;
query = "insert into ijbook values (?,?)";
PreparedStatement pstmt;

pstmt = conn.PreparedStatement(query);
pstmt.setString(1, name);
pstmt.setString(2, phone.toString());
pstmt.execute();

query = "select * from ijbook";
ResultSet rs = stmt.executeQuery(query);

while( rs.next() )
{
	string x=rs.getString("name");
	string y=rs.getString("phone");
	out.print(x + y);
}
rs.close();
stmt.close();
conn.close();
%>
</body>
</head>
</html>