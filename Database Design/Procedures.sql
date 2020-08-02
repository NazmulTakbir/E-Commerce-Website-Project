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
	
	score := UTL_MATCH.edit_distance_similarity( search_string, product_string )/100;
	IF score > similarity_score AND score >= 0.7 THEN
			similarity_score := score;
	END IF;
	
	RETURN similarity_score;
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

CREATE OR REPLACE FUNCTION ORDER_TOTAL(O_ID IN NUMBER)
RETURN NUMBER IS
	total_amount NUMBER := 0;
	temp NUMBER;
	temp2 NUMBER;
BEGIN
	
	SELECT SUM(B.PRICE) INTO total_amount FROM 
	( SELECT PRODUCT_ID, SELLER_ID FROM ORDERED_ITEMS WHERE ORDER_ID = O_ID ) A
	JOIN PRODUCT B ON (A.PRODUCT_ID=B.PRODUCT_ID AND A.SELLER_ID=B.SELLER_ID );
	
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

CREATE OR REPLACE FUNCTION WALLET_BALANCE(ID IN NUMBER, AC_TYPE IN VARCHAR2)
RETURN NUMBER IS
	balance NUMBER := 0;
	temp NUMBER;
BEGIN
	
	IF AC_TYPE = 'CUSTOMER' THEN
		
		SELECT SUM( ORDER_TOTAL(ORDER_ID) ) INTO temp FROM CUSTOMER_ORDER
		JOIN PURCHASE_ORDER USING(ORDER_ID) WHERE LOWER(PAYMENT_METHOD) = 'wallet'
		AND CUSTOMER_ID = ID;
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
		USING(ORDER_ID) WHERE ( LOWER(DELIVERY_STATUS) = 'delivered' OR 
	  LOWER(PAYMENT_METHOD) = 'wallet' ) AND SELLER_ID = ID;	
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