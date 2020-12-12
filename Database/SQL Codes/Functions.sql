CREATE OR REPLACE FUNCTION STRING_SIMILARITY(search_string IN VARCHAR2, product_string IN VARCHAR2, delimiter IN VARCHAR2 DEFAULT ' ')
RETURN NUMBER IS
	TYPE words IS VARRAY(150) OF VARCHAR2(150);
	search_words words := words();
	product_words words := words();
	i NUMBER;
	j NUMBER;
	score NUMBER;
	similarity_score NUMBER := 0;
	sw_count NUMBER := 0;
	pw_count NUMBER := 0;
	current_delimiter NUMBER;
	previous_delimiter NUMBER;
	temp VARCHAR2(150);
BEGIN

	i := 1;
	current_delimiter := 0;
	previous_delimiter := 0;
	
	WHILE i <= LENGTH(search_string)
	LOOP
	
		IF SUBSTR(search_string, i, 1) = delimiter THEN
			current_delimiter := i;
			temp := SUBSTR( search_string, previous_delimiter+1, current_delimiter-previous_delimiter-1 );
			search_words.extend(1);
			sw_count := sw_count + 1;
			search_words(sw_count) := temp;
			previous_delimiter := current_delimiter;
		END IF;
		
		i := i + 1;
	END LOOP;
	
	temp := SUBSTR( search_string, previous_delimiter+1, LENGTH(search_string)-previous_delimiter );
	search_words.extend(1);
	sw_count := sw_count + 1;
	search_words(sw_count) := temp;
	
	
	
	
	i := 1;
	current_delimiter := 0;
	previous_delimiter := 0;
	
	WHILE i <= LENGTH(product_string)
	LOOP
	
		IF SUBSTR(product_string, i, 1) = delimiter THEN
			current_delimiter := i;
			temp := SUBSTR( product_string, previous_delimiter+1, current_delimiter-previous_delimiter-1 );
			product_words.extend(1);
			pw_count := pw_count + 1;
			product_words(pw_count) := temp;
			previous_delimiter := current_delimiter;
		END IF;
		
		i := i + 1;
	END LOOP;
	
	temp := SUBSTR( product_string, previous_delimiter+1, LENGTH(product_string)-previous_delimiter );
	product_words.extend(1);
	pw_count := pw_count + 1;
	product_words(pw_count) := temp;

	i := 1;
	WHILE i <= sw_count
	LOOP
		score := 0;
		
		IF LOWER(product_string) LIKE CONCAT( CONCAT( '%', LOWER(search_words(i)) ), '%' ) THEN
			score := 1;
		ELSE
			j := 1;
			WHILE j <= pw_count
			LOOP
				IF UTL_MATCH.edit_distance_similarity( LOWER(search_words(i)), LOWER(product_words(j)) ) > score THEN
					score := UTL_MATCH.edit_distance_similarity( LOWER(search_words(i)), LOWER(product_words(j)) );
				END IF;
				j := j + 1;
			END LOOP;
			
			score := score/100;
			
		END IF;
		
		IF score >= 0.7 THEN
			similarity_score := similarity_score + score;
		END IF;
		
		i := i + 1;
		
	END LOOP;
	
	
	i := 1;
	WHILE i <= pw_count
	LOOP
		score := 0;
		
		IF LOWER(search_string) LIKE CONCAT( CONCAT( '%', LOWER(product_words(i)) ), '%' ) THEN
			score := 1;
		ELSE
			j := 1;
			WHILE j <= sw_count
			LOOP
				IF UTL_MATCH.edit_distance_similarity( LOWER(product_words(i)), LOWER(search_words(j)) ) > score THEN
					score := UTL_MATCH.edit_distance_similarity( LOWER(product_words(i)), LOWER(search_words(j)) );
				END IF;
				j := j + 1;
			END LOOP;
			
			score := score/100;
			
		END IF;
		
		IF score >= 0.7 THEN
			similarity_score := similarity_score + score;
		END IF;
		
		i := i + 1;
		
	END LOOP;
	
	
	
	
	score := UTL_MATCH.edit_distance_similarity( search_string, product_string )/100;
	IF score > similarity_score AND score >= 0.7 THEN
			similarity_score := score;
	END IF;
	
	RETURN similarity_score;
END ;
/


CREATE OR REPLACE FUNCTION WALLET_BALANCE(ID IN NUMBER, AC_TYPE IN VARCHAR2)
RETURN NUMBER IS
	balance NUMBER := 0;
	temp NUMBER;
BEGIN
	
	IF AC_TYPE = 'CUSTOMER' THEN
		
		SELECT SUM( ORDER_TOTAL(ORDER_ID) ) INTO temp FROM CUSTOMER_ORDER
		JOIN PURCHASE_ORDER USING(ORDER_ID) WHERE LOWER(PAYMENT_METHOD) = 'wallet' AND 
		(LOWER(DELIVERY_STATUS)	='delivered' OR LOWER(DELIVERY_STATUS) = 'returned' OR 
		LOWER(DELIVERY_STATUS) = 'not delivered') AND CUSTOMER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance - temp; 
		END IF;
	
		SELECT SUM( ORDER_TOTAL(ORDER_ID) ) INTO temp FROM CUSTOMER_ORDER 
		JOIN RETURN_ORDER USING(ORDER_ID) WHERE LOWER(APPROVAL_STATUS) = 'approved' 
		AND CUSTOMER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance + temp; 
		END IF;
		
		SELECT SUM(AMOUNT) INTO temp FROM TRANSACTIONS JOIN CUSTOMER_WALLET_RECHARGE 
		USING(TRANSACTION_ID) WHERE CUSTOMER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance + temp; 
		END IF;
	
	ELSIF AC_TYPE = 'SELLER' THEN
		
		SELECT SUM(COST_FOR_SELLER) INTO temp FROM ADVERTISEMENT
		WHERE SELLER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance - temp; 
		END IF;
		
		SELECT SUM( ORDER_TOTAL(ORDER_ID) ) INTO temp FROM CUSTOMER_ORDER JOIN PURCHASE_ORDER
		USING(ORDER_ID) WHERE ( ( LOWER(PAYMENT_METHOD) = 'cash' AND ( LOWER(DELIVERY_STATUS) = 'delivered' 
		OR LOWER(DELIVERY_STATUS) = 'returned') )
		OR ( LOWER(PAYMENT_METHOD) = 'wallet' AND LOWER(DELIVERY_STATUS) != 'cancelled' ) ) AND SELLER_ID = ID;	
		IF NOT temp IS NULL THEN
			balance := balance + temp; 
		END IF;

	  SELECT SUM( ORDER_TOTAL(ORDER_ID) ) INTO temp FROM CUSTOMER_ORDER JOIN RETURN_ORDER
		USING(ORDER_ID) WHERE LOWER(APPROVAL_STATUS) = 'approved' AND SELLER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance - temp; 
		END IF;
		
		SELECT SUM(AMOUNT) INTO temp FROM SELLER_TRANSACTION JOIN TRANSACTIONS USING(TRANSACTION_ID)
		WHERE SELLER_ID = ID;
		IF NOT temp IS NULL THEN
			balance := balance + temp; 
		END IF;
		
	END IF;
	
	RETURN balance;
	
END ;
/


CREATE OR REPLACE FUNCTION AVG_RATING(P_ID IN NUMBER, S_ID IN NUMBER)
RETURN NUMBER IS
	RESULT NUMBER;
BEGIN 
	SELECT ROUND(AVG(RATING),1) INTO RESULT FROM REVIEW WHERE PRODUCT_ID = P_ID AND SELLER_ID = S_ID ;
	RETURN RESULT;
END;
/


CREATE OR REPLACE FUNCTION MAX_DISCOUNT(P_ID IN NUMBER, S_ID IN NUMBER)
RETURN NUMBER IS
	RESULT NUMBER;
BEGIN 
	SELECT MAX(PERCENTAGE_DISCOUNT) INTO RESULT FROM OFFER WHERE PRODUCT_ID = P_ID AND SELLER_ID = S_ID AND START_DATE <= SYSDATE AND END_DATE >= SYSDATE;
	RETURN RESULT;
END;
/


CREATE OR REPLACE FUNCTION ORDER_TOTAL(O_ID IN NUMBER)
RETURN NUMBER IS
	total_amount NUMBER := 0;
	total_amount2 NUMBER := 0;
	temp NUMBER;
	temp2 NUMBER;
BEGIN
	
	SELECT SUM(B.PRICE) INTO total_amount FROM 
	( SELECT PRODUCT_ID, SELLER_ID FROM ORDERED_ITEMS WHERE ORDER_ID = O_ID ) A
	JOIN PRODUCT B ON (A.PRODUCT_ID=B.PRODUCT_ID AND A.SELLER_ID=B.SELLER_ID );
	
	SELECT SUM(B.PRICE) INTO total_amount2 FROM
	( SELECT PRODUCT_ID, SELLER_ID FROM ORDERED_ITEMS WHERE ORDER_ID = O_ID) A
	JOIN PRODUCT_HISTORY B ON (A.PRODUCT_ID=B.PRODUCT_ID AND A.SELLER_ID=B.SELLER_ID ) 
	WHERE B.START_DATE <= (SELECT ORDER_DATE FROM CUSTOMER_ORDER WHERE ORDER_ID = O_ID) AND      
	B.END_DATE >= (SELECT ORDER_DATE FROM CUSTOMER_ORDER WHERE ORDER_ID = O_ID);
	
	IF total_amount2 IS NOT NULL THEN
		total_amount := total_amount2;
	END IF;
	
	SELECT COUNT(*) INTO temp2 FROM ORDERED_ITEMS WHERE ORDER_ID = ORDER_ID; 
	
	SELECT MAX(PERCENTAGE_DISCOUNT) INTO temp FROM OFFER JOIN ORDERED_ITEMS 
	USING(PRODUCT_ID, SELLER_ID) JOIN CUSTOMER_ORDER USING(ORDER_ID) 
	WHERE ORDER_ID = O_ID AND START_DATE <= ORDER_DATE AND END_DATE>=ORDER_DATE 
	AND temp2 >= MINIMUM_QUANTITY_PURCHASED;
	
	IF NOT temp IS NULL THEN
		total_amount := total_amount * (1-temp/100); 
	END IF;
	
	total_amount := FLOOR( total_amount );
	
	RETURN total_amount;
	
END ;
/


CREATE OR REPLACE FUNCTION ORDER_STATUS(ID IN NUMBER)
RETURN VARCHAR2 IS
	temp NUMBER;
	status VARCHAR2(30);
BEGIN

	SELECT COUNT(*) INTO temp FROM RETURN_ORDER
	WHERE ORDER_ID = ID;
	
	IF temp = 1 THEN
	
		SELECT APPROVAL_STATUS INTO status FROM RETURN_ORDER 
		WHERE ORDER_ID = ID;
		
	ELSE
	
		SELECT DELIVERY_STATUS INTO status FROM PURCHASE_ORDER
		WHERE ORDER_ID = ID;
	
	END IF;
	
	RETURN status;
	
END;
/


CREATE OR REPLACE FUNCTION HAVERSINE(OID IN NUMBER)
RETURN NUMBER IS
	LOCATION1 VARCHAR2(100);
	LOCATION2 VARCHAR2(100);
	POS NUMBER;
	LAT1 NUMBER;
	LAT2 NUMBER;
	LON1 NUMBER;
	LON2 NUMBER;
	DIF1 NUMBER;
	DIF2 NUMBER;
	DIS NUMBER;
	PI NUMBER;
	DIS_MIN NUMBER;
	ID NUMBER;
BEGIN
	SELECT LOCATION INTO LOCATION1 FROM SELLER WHERE SELLER_ID = 
	(SELECT SELLER_ID FROM CUSTOMER_ORDER WHERE ORDER_ID = OID); 
	PI := 3.14159265358979;
	DIS_MIN := PI * 6371;
	POS := INSTR(LOCATION1 , ',');
	LAT1 := SUBSTR(LOCATION1, 1, POS-1);
	LON1 := SUBSTR(LOCATION1, POS+1);
	LAT1 := LAT1 * PI / 180;
	FOR R IN (SELECT CURRENT_LOCATION, EMPLOYEE_ID FROM DELIVERY_GUY )
	LOOP
		LOCATION2 := R.CURRENT_LOCATION;
		POS := INSTR(LOCATION2 , ',');
		LAT2 := SUBSTR(LOCATION2, 1, POS-1);
		LON2 := SUBSTR(LOCATION2, POS+1);
		DIF1 := (LAT1 - LAT2) * PI / 180;
		DIF2 := (LON1 - LON2) * PI / 180;
		LAT2 := LAT2 * PI /180;
		DIS := POWER(SIN(DIF1/2), 2) + POWER(SIN(DIF2/2), 2) * COS(LAT1) * COS(LAT2);
		DIS := ROUND(2 * 6371 * ASIN(SQRT(DIS)), 5);
		IF DIS_MIN > DIS THEN
			DIS_MIN := DIS;
			ID := R.EMPLOYEE_ID;
		END IF;
	END LOOP ;
	RETURN ID;
END ;
/