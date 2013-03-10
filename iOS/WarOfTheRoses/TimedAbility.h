//
//  TimedAbility.h
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 3/4/13.
//
//

#import <Foundation/Foundation.h>

@class TimedAbility;
@protocol TimedAbilityDelegate <NSObject>

@optional

- (void)timedAbilityWillStart:(TimedAbility*)timedAbility;
- (void)timedAbilityDidStart:(TimedAbility*)timedAbility;

- (void)timedAbilityWillStop:(TimedAbility*)timedAbility;
- (void)timedAbilityDidStop:(TimedAbility*)timedAbility;

@end

@class Card;
@interface TimedAbility : NSObject {
    
    Card *_card;
    NSUInteger _abilityStartedInRound;
}

@property (nonatomic, readonly) NSUInteger numberOfRounds;
@property (nonatomic, weak) id<TimedAbilityDelegate> delegate;

- (id)initForNumberOfRounds:(NSUInteger)numberOfRounds onCard:(Card*)card;

- (void)startTimedAbility;
- (void)stopTimedAbility;

@end